-- -----------------------------------------------------
-- Table installation
-- -----------------------------------------------------
CREATE TABLE installation (
  id SERIAL,
  unique_id VARCHAR(32) UNIQUE NOT NULL,
  PRIMARY KEY (id));


-- -----------------------------------------------------
-- Table execution_description
-- -----------------------------------------------------
CREATE TABLE execution_description (
  id SERIAL,
  installation_id INT NOT NULL,
  execution_timestamp TIMESTAMP NOT NULL,
  toolbox_launched BOOL NOT NULL,
  queue_type VARCHAR(64) NULL,
  fp_set_type VARCHAR(64) NULL,
  off_heap_memory INT NOT NULL,
  heap_memory INT NOT NULL,
  jvm_architecture VARCHAR(8) NOT NULL,
  jvm_version VARCHAR(12) NOT NULL,
  jvm_vendor VARCHAR(64) NOT NULL,
  os_architecture VARCHAR(8) NOT NULL,
  os_version VARCHAR(48) NOT NULL,
  os_name VARCHAR(24) NOT NULL,
  core_count INT NOT NULL,
  worker_count INT NOT NULL,
  mode VARCHAR(16) NOT NULL,
  version VARCHAR(16) NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (installation_id) REFERENCES installation (id));
