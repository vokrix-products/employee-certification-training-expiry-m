-- VOKRIX RLS TEMPLATE — applied once per product by Build Specialist's brief.
-- Replace {table_name} with the real table for that product
-- (e.g. coi_certificates, ar_invoices, claims).
--
-- Every product table in the shared vokrix-products-db Supabase project
-- MUST follow this exact pattern: product_id + customer_id columns,
-- RLS scoped to both. This is what makes one shared project safe for
-- many products and many customers.

-- 1. Required columns (add alongside the product's real domain columns)
-- product_id text NOT NULL
-- customer_id uuid NOT NULL

-- 2. Enable RLS
ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;

-- 3. Policy — customer sees/writes only their own rows for this specific product
-- USING controls SELECT/UPDATE/DELETE visibility.
-- WITH CHECK controls INSERT/UPDATE — without it, INSERT fails even when USING allows reads.
CREATE POLICY "customers see only their own product data"
ON {table_name}
FOR ALL
USING (
  customer_id = auth.uid()
  AND product_id = (auth.jwt() -> 'app_metadata' ->> 'product_id')
)
WITH CHECK (
  customer_id = auth.uid()
  AND product_id = (auth.jwt() -> 'app_metadata' ->> 'product_id')
);

-- 4. Grants — RLS alone is not enough, role needs base table grants too
GRANT SELECT, INSERT, UPDATE, DELETE ON {table_name} TO authenticated;
GRANT SELECT ON {table_name} TO anon;
