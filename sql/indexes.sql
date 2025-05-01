CREATE INDEX idx_payments_status_paidat
  ON payments(status, paid_at);

CREATE INDEX idx_impdec_user_date
  ON import_declarations(user_id, declaration_date);

CREATE INDEX idx_products_country
  ON products(country_id);

CREATE INDEX idx_products_category
  ON products(category_id);

CREATE INDEX idx_tariffrate_lookup
  ON tariff_rates(country_id, category_id, effective_from DESC);