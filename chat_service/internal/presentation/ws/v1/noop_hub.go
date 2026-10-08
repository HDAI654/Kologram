package v1

// NoOpHub discards register/unregister (tests / before realtime hub is wired).
type NoOpHub struct{}

func (NoOpHub) Register(*Session)   {}
func (NoOpHub) Unregister(*Session) {}
