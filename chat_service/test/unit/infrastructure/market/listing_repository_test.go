package market_test

import (
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"net/http/httptest"
	"testing"

	domainerrors "github.com/HDAI654/Kologram/chat_service/internal/domain/errors"
	"github.com/HDAI654/Kologram/chat_service/internal/domain/valueobjects"
	"github.com/HDAI654/Kologram/chat_service/internal/infrastructure/market"
)

func TestListingRepository_ActiveListing(t *testing.T) {
	t.Parallel()

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path != "/graphql" || r.Method != http.MethodPost {
			t.Fatalf("unexpected %s %s", r.Method, r.URL.Path)
		}
		_ = json.NewEncoder(w).Encode(map[string]any{
			"data": map[string]any{
				"listing": map[string]any{
					"listingId": "431f7a61-1a30-4c3a-b2d4-5282ca2799b5",
					"status":    "ACTIVE",
					"sellerId":  "bdf038e5-8b16-4825-a895-ce7d0648e845",
				},
			},
		})
	}))
	defer srv.Close()

	repo := market.NewListingRepository(srv.URL, srv.Client())
	id, _ := valueobjects.NewListingID("431f7a61-1a30-4c3a-b2d4-5282ca2799b5")
	listing, err := repo.GetByID(context.Background(), id)
	if err != nil {
		t.Fatalf("GetByID: %v", err)
	}
	if listing == nil || !listing.MessageAllowed {
		t.Fatalf("listing = %+v", listing)
	}
}

func TestListingRepository_SoldNotMessageable(t *testing.T) {
	t.Parallel()

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		_ = json.NewEncoder(w).Encode(map[string]any{
			"data": map[string]any{
				"listing": map[string]any{
					"listingId": "431f7a61-1a30-4c3a-b2d4-5282ca2799b5",
					"status":    "SOLD",
					"sellerId":  "bdf038e5-8b16-4825-a895-ce7d0648e845",
				},
			},
		})
	}))
	defer srv.Close()

	repo := market.NewListingRepository(srv.URL, srv.Client())
	id, _ := valueobjects.NewListingID("431f7a61-1a30-4c3a-b2d4-5282ca2799b5")
	listing, err := repo.GetByID(context.Background(), id)
	if err != nil {
		t.Fatalf("GetByID: %v", err)
	}
	if listing.MessageAllowed {
		t.Fatalf("SOLD must not allow messaging")
	}
}

func TestListingRepository_NotFound(t *testing.T) {
	t.Parallel()

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		_ = json.NewEncoder(w).Encode(map[string]any{
			"errors": []map[string]any{
				{"message": "not found", "extensions": map[string]any{"code": "NOT_FOUND"}},
			},
		})
	}))
	defer srv.Close()

	repo := market.NewListingRepository(srv.URL, srv.Client())
	id, _ := valueobjects.NewListingID("431f7a61-1a30-4c3a-b2d4-5282ca2799b5")
	listing, err := repo.GetByID(context.Background(), id)
	if err != nil || listing != nil {
		t.Fatalf("listing=%v err=%v", listing, err)
	}
}

func TestListingRepository_ValidationError(t *testing.T) {
	t.Parallel()

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		_ = json.NewEncoder(w).Encode(map[string]any{
			"errors": []map[string]any{
				{"message": "bad id", "extensions": map[string]any{"code": "VALIDATION_ERROR"}},
			},
		})
	}))
	defer srv.Close()

	repo := market.NewListingRepository(srv.URL, srv.Client())
	id, _ := valueobjects.NewListingID("431f7a61-1a30-4c3a-b2d4-5282ca2799b5")
	_, err := repo.GetByID(context.Background(), id)
	var ve *domainerrors.ValidationError
	if !errors.As(err, &ve) {
		t.Fatalf("err = %v, want ValidationError", err)
	}
}

func TestListingRepository_HTTPFailure(t *testing.T) {
	t.Parallel()

	srv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusBadGateway)
	}))
	defer srv.Close()

	repo := market.NewListingRepository(srv.URL, srv.Client())
	id, _ := valueobjects.NewListingID("431f7a61-1a30-4c3a-b2d4-5282ca2799b5")
	_, err := repo.GetByID(context.Background(), id)
	var es *domainerrors.ExternalServiceError
	if !errors.As(err, &es) {
		t.Fatalf("err = %v, want ExternalServiceError", err)
	}
}
