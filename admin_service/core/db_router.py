"""Route Auth models → auth DB, Market models → market DB."""

from __future__ import annotations


class KologramDatabaseRouter:

    auth_models = {"authuser"}
    market_models = {"category", "listing", "listingimage"}

    def db_for_read(self, model, **hints):
        name = model._meta.model_name
        if name in self.auth_models:
            return "auth"
        if name in self.market_models:
            return "market"
        return "default"

    def db_for_write(self, model, **hints):
        return self.db_for_read(model, **hints)

    def allow_relation(self, obj1, obj2, **hints):
        db1 = self.db_for_read(obj1.__class__)
        db2 = self.db_for_read(obj2.__class__)
        if db1 == db2:
            return True
        # Allow relations only within the same physical DB.
        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # External service tables are unmanaged — never migrate them.
        if model_name in self.auth_models | self.market_models:
            return False
        # Django's own tables only on default.
        if db == "default":
            return model_name not in self.auth_models | self.market_models
        return False
