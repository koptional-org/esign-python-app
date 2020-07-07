
drop table if exists projects;
create table projects (
  id integer primary key autoincrement,
  'contact_email' varchar(255) not null,
  'contact_name' varchar(255) not null,
  'contract_type' varchar(255) not null,
  'quote_dollars' int not null,
  'signed_pdf' int DEFAULT 0,
  'is_complete' int DEFAULT 0
);