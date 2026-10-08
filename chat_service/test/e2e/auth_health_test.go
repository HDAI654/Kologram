package e2e_test

import (
	"encoding/json"
	"net/http"
	"testing"
)

func TestE2E_Health(t *testing.T) {
	t.Parallel()
	h := newHarness(t)
	resp, err := http.Get(h.server.URL + "/health")
	if err != nil {
		t.Fatal(err)
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		t.Fatalf("status=%d", resp.StatusCode)
	}
	var body map[string]string
	_ = json.NewDecoder(resp.Body).Decode(&body)
	if body["status"] != "ok" {
		t.Fatalf("body=%v", body)
	}
}

func TestE2E_WS_MissingUserID(t *testing.T) {
	t.Parallel()
	h := newHarness(t)
	h.dialExpectHTTP(t, "", http.StatusUnauthorized)
}

func TestE2E_WS_InvalidUserID(t *testing.T) {
	t.Parallel()
	h := newHarness(t)
	h.dialExpectHTTP(t, "not-uuid", http.StatusUnauthorized)
}

func TestE2E_WS_UnknownAction(t *testing.T) {
	t.Parallel()
	h := newHarness(t)
	c := h.dial(t, buyerID, false)
	c.mustErr("1", "nope", map[string]any{}, "INVALID_REQUEST")
}
