-- Bro Code Fashion: initial private business database
-- Apply this migration in the Supabase SQL Editor.
-- This creates the schema only; it does not add real products or stock quantities.

create extension if not exists pgcrypto;

create table if not exists public.admin_users (
  user_id uuid primary key references auth.users(id) on delete cascade,
  created_at timestamptz not null default now()
);

create or replace function public.is_bcf_admin()
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1
    from public.admin_users
    where user_id = auth.uid()
  );
$$;

revoke all on function public.is_bcf_admin() from public;
grant execute on function public.is_bcf_admin() to authenticated;

create table if not exists public.sales_channels (
  id uuid primary key default gen_random_uuid(),
  code text not null unique,
  name text not null,
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists public.products (
  id uuid primary key default gen_random_uuid(),
  product_code text not null unique,
  name text not null,
  description text,
  colour text,
  status text not null default 'active'
    check (status in ('active', 'draft', 'archived')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.product_variants (
  id uuid primary key default gen_random_uuid(),
  product_id uuid not null references public.products(id) on delete restrict,
  sku text not null unique,
  size text not null,
  selling_price numeric(12,2) check (selling_price is null or selling_price >= 0),
  unit_cost numeric(12,2) check (unit_cost is null or unit_cost >= 0),
  is_active boolean not null default true,
  created_at timestamptz not null default now(),
  unique (product_id, size)
);

create table if not exists public.inventory (
  variant_id uuid primary key references public.product_variants(id) on delete restrict,
  quantity_on_hand integer not null default 0 check (quantity_on_hand >= 0),
  quantity_reserved integer not null default 0 check (quantity_reserved >= 0),
  updated_at timestamptz not null default now(),
  check (quantity_reserved <= quantity_on_hand)
);

create table if not exists public.customers (
  id uuid primary key default gen_random_uuid(),
  full_name text not null,
  phone text not null,
  email text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.orders (
  id uuid primary key default gen_random_uuid(),
  order_number text not null unique,
  channel_id uuid not null references public.sales_channels(id) on delete restrict,
  customer_id uuid references public.customers(id) on delete set null,
  status text not null default 'pending_confirmation'
    check (status in ('pending_confirmation', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'returned')),
  payment_status text not null default 'unpaid'
    check (payment_status in ('unpaid', 'pending', 'partially_paid', 'paid', 'refunded')),
  payment_method text,
  subtotal numeric(12,2) not null default 0 check (subtotal >= 0),
  shipping_fee numeric(12,2) not null default 0 check (shipping_fee >= 0),
  discount numeric(12,2) not null default 0 check (discount >= 0),
  total numeric(12,2) not null default 0 check (total >= 0),
  external_order_id text,
  customer_name_snapshot text,
  customer_phone_snapshot text,
  delivery_address text,
  delivery_city text,
  delivery_pincode text,
  customer_notes text,
  internal_notes text,
  placed_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create unique index if not exists orders_channel_external_id_unique
  on public.orders (channel_id, external_order_id)
  where external_order_id is not null;

create table if not exists public.order_items (
  id uuid primary key default gen_random_uuid(),
  order_id uuid not null references public.orders(id) on delete cascade,
  product_id uuid references public.products(id) on delete set null,
  variant_id uuid references public.product_variants(id) on delete set null,
  product_name_snapshot text not null,
  sku_snapshot text,
  size_snapshot text,
  quantity integer not null check (quantity > 0),
  unit_price numeric(12,2) not null check (unit_price >= 0),
  line_total numeric(12,2) not null check (line_total >= 0),
  created_at timestamptz not null default now()
);

create table if not exists public.inventory_movements (
  id uuid primary key default gen_random_uuid(),
  variant_id uuid not null references public.product_variants(id) on delete restrict,
  movement_type text not null
    check (movement_type in ('opening_stock', 'purchase', 'sale', 'reservation', 'release', 'return', 'adjustment', 'damage')),
  quantity_change integer not null check (quantity_change <> 0),
  reference_type text,
  reference_id uuid,
  reason text,
  created_by uuid references auth.users(id) on delete set null,
  created_at timestamptz not null default now()
);

create table if not exists public.payments (
  id uuid primary key default gen_random_uuid(),
  order_id uuid not null references public.orders(id) on delete restrict,
  amount numeric(12,2) not null check (amount > 0),
  method text not null,
  status text not null default 'pending'
    check (status in ('pending', 'successful', 'failed', 'refunded')),
  transaction_reference text,
  paid_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists public.expenses (
  id uuid primary key default gen_random_uuid(),
  expense_date date not null default current_date,
  category text not null,
  description text not null,
  amount numeric(12,2) not null check (amount > 0),
  payment_method text,
  reference_number text,
  notes text,
  created_by uuid references auth.users(id) on delete set null,
  created_at timestamptz not null default now()
);

create index if not exists product_variants_product_id_idx on public.product_variants(product_id);
create index if not exists orders_placed_at_idx on public.orders(placed_at desc);
create index if not exists orders_status_idx on public.orders(status);
create index if not exists orders_channel_id_idx on public.orders(channel_id);
create index if not exists order_items_order_id_idx on public.order_items(order_id);
create index if not exists inventory_movements_variant_created_idx on public.inventory_movements(variant_id, created_at desc);
create index if not exists expenses_expense_date_idx on public.expenses(expense_date desc);

insert into public.sales_channels (code, name) values
  ('website', 'Website'),
  ('whatsapp', 'WhatsApp'),
  ('roadside_stall', 'Roadside Stall'),
  ('meesho', 'Meesho'),
  ('flipkart', 'Flipkart'),
  ('amazon', 'Amazon'),
  ('instagram_facebook', 'Instagram / Facebook')
on conflict (code) do update set name = excluded.name;

-- Enable row-level security on every business table.
alter table public.admin_users enable row level security;
alter table public.sales_channels enable row level security;
alter table public.products enable row level security;
alter table public.product_variants enable row level security;
alter table public.inventory enable row level security;
alter table public.customers enable row level security;
alter table public.orders enable row level security;
alter table public.order_items enable row level security;
alter table public.inventory_movements enable row level security;
alter table public.payments enable row level security;
alter table public.expenses enable row level security;

-- Only the matching signed-in admin can see their own admin membership.
drop policy if exists "admin can read own membership" on public.admin_users;
create policy "admin can read own membership"
  on public.admin_users for select to authenticated
  using (user_id = auth.uid());

-- Business data is accessible only to users explicitly registered in admin_users.
do $$
declare
  table_name text;
begin
  foreach table_name in array array[
    'sales_channels',
    'products',
    'product_variants',
    'inventory',
    'customers',
    'orders',
    'order_items',
    'inventory_movements',
    'payments',
    'expenses'
  ]
  loop
    execute format('drop policy if exists "bcf admin full access" on public.%I', table_name);
    execute format(
      'create policy "bcf admin full access" on public.%I for all to authenticated using (public.is_bcf_admin()) with check (public.is_bcf_admin())',
      table_name
    );
  end loop;
end $$;

-- Do not expose business tables to anonymous visitors.
revoke all on public.admin_users, public.sales_channels, public.products,
  public.product_variants, public.inventory, public.customers, public.orders,
  public.order_items, public.inventory_movements, public.payments, public.expenses
  from anon;

grant select on public.admin_users to authenticated;
grant select, insert, update, delete on public.sales_channels, public.products,
  public.product_variants, public.inventory, public.customers, public.orders,
  public.order_items, public.inventory_movements, public.payments, public.expenses
  to authenticated;
