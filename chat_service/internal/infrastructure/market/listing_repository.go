package market

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"

	"github.com/HDAI654/Kologram/chat_service/internal/domain/entities"
	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/ports"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
)

const defaultTimeout = 5 * time.Second

// ListingRepository resolves listings via the market service GraphQL API.
// MessageAllowed is true only when listing status is ACTIVE.
type ListingRepository struct {
	baseURL    string
	httpClient *http.Client
}

// NewListingRepository builds a market listing adapter.
// baseURL is the market service origin (e.g. http://market:8080), without /graphql.
func NewListingRepository(baseURL string, httpClient *http.Client) *ListingRepository {
	baseURL = strings.TrimRight(strings.TrimSpace(baseURL), "/")
	if httpClient == nil {
		httpClient = &http.Client{Timeout: defaultTimeout}
	}
	return &ListingRepository{baseURL: baseURL, httpClient: httpClient}
}

var _ ports.ListingRepository = (*ListingRepository)(nil)

type graphqlRequest struct {
	Query     string         `json:"query"`
	Variables map[string]any `json:"variables,omitempty"`
}

type listingGQLResponse struct {
	Data *struct {
		Listing *struct {
			ListingID string `json:"listingId"`
			Status    string `json:"status"`
			SellerID  string `json:"sellerId"`
		} `json:"listing"`
	} `json:"data"`
	Errors []struct {
		Message    string `json:"message"`
		Extensions struct {
			Code string `json:"code"`
		} `json:"extensions"`
	} `json:"errors"`
}

const listingQuery = `
query Listing($listingId: ID!) {
  listing(listingId: $listingId) {
    listingId
    status
    sellerId
  }
}`

// GetByID returns (nil, nil) when the listing does not exist (NOT_FOUND / null data).
func (r *ListingRepository) GetByID(
	ctx context.Context,
	listingID valueobjects.ListingID,
) (*entities.Listing, error) {
	if r.baseURL == "" {
		return nil, &domainerrors.ExternalServiceError{
			Service: "market",
			Message: "base URL is not configured",
		}
	}

	body, err := json.Marshal(graphqlRequest{
		Query:     listingQuery,
		Variables: map[string]any{"listingId": listingID.String()},
	})
	if err != nil {
		return nil, &domainerrors.ExternalServiceError{
			Service: "market",
			Message: "encode request",
			Err:     err,
		}
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, r.baseURL+"/graphql", bytes.NewReader(body))
	if err != nil {
		return nil, &domainerrors.ExternalServiceError{
			Service: "market",
			Message: "build request",
			Err:     err,
		}
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Accept", "application/json")

	resp, err := r.httpClient.Do(req)
	if err != nil {
		if ctx.Err() != nil {
			return nil, &domainerrors.ExternalServiceError{
				Service: "market",
				Message: "request timeout or canceled",
				Err:     err,
			}
		}
		return nil, &domainerrors.ExternalServiceError{
			Service: "market",
			Message: "request failed",
			Err:     err,
		}
	}
	defer resp.Body.Close()

	raw, err := io.ReadAll(io.LimitReader(resp.Body, 1<<20))
	if err != nil {
		return nil, &domainerrors.ExternalServiceError{
			Service: "market",
			Message: "read response",
			Err:     err,
		}
	}

	// Market GraphQL uses HTTP 200 with errors in the body; non-200 is unexpected.
	if resp.StatusCode != http.StatusOK {
		return nil, &domainerrors.ExternalServiceError{
			Service: "market",
			Message: fmt.Sprintf("unexpected HTTP status %d", resp.StatusCode),
		}
	}

	var parsed listingGQLResponse
	if err := json.Unmarshal(raw, &parsed); err != nil {
		return nil, &domainerrors.ExternalServiceError{
			Service: "market",
			Message: "decode response",
			Err:     err,
		}
	}

	if code := firstErrorCode(parsed.Errors); code != "" {
		switch code {
		case "NOT_FOUND":
			return nil, nil
		case "VALIDATION_ERROR":
			return nil, &domainerrors.ValidationError{
				Field:   "listing_id",
				Message: firstErrorMessage(parsed.Errors),
			}
		default:
			return nil, &domainerrors.ExternalServiceError{
				Service: "market",
				Message: firstErrorMessage(parsed.Errors),
			}
		}
	}

	if parsed.Data == nil || parsed.Data.Listing == nil {
		return nil, nil
	}

	l := parsed.Data.Listing
	id, err := valueobjects.NewListingID(l.ListingID)
	if err != nil {
		return nil, &domainerrors.ExternalServiceError{
			Service: "market",
			Message: "invalid listingId in response",
			Err:     err,
		}
	}
	sellerID, err := valueobjects.NewUserID(l.SellerID)
	if err != nil {
		return nil, &domainerrors.ExternalServiceError{
			Service: "market",
			Message: "invalid sellerId in response",
			Err:     err,
		}
	}

	return &entities.Listing{
		ID:             id,
		SellerID:       sellerID,
		MessageAllowed: strings.EqualFold(strings.TrimSpace(l.Status), "ACTIVE"),
	}, nil
}

func firstErrorCode(errs []struct {
	Message    string `json:"message"`
	Extensions struct {
		Code string `json:"code"`
	} `json:"extensions"`
}) string {
	if len(errs) == 0 {
		return ""
	}
	return strings.ToUpper(strings.TrimSpace(errs[0].Extensions.Code))
}

func firstErrorMessage(errs []struct {
	Message    string `json:"message"`
	Extensions struct {
		Code string `json:"code"`
	} `json:"extensions"`
}) string {
	if len(errs) == 0 {
		return "unknown market error"
	}
	if errs[0].Message != "" {
		return errs[0].Message
	}
	return errs[0].Extensions.Code
}
