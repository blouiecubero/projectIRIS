BEGIN TRANSACTION;
CREATE TABLE userstatistics (
	id INTEGER NOT NULL, 
	"userId" INTEGER, 
	vl INTEGER, 
	"vlDates" BLOB, 
	sl INTEGER, 
	"slDates" BLOB, 
	"offset" INTEGER, 
	"offsetDates" BLOB, "offsetDatesRecord" BLOB, "slDatesRecord" BLOB, "vlDatesRecord" BLOB, "offestDatesCancelled" BLOB, "slDatesCancelled" BLOB, "vlDatesCancelled" BLOB, "offsetDatesAppliedDates" BLOB, "offsetDatesDecidedDates" BLOB, "slDatesAppliedDates" BLOB, "slDatesDecidedDates" BLOB, "vlDatesAppliedDates" BLOB, "vlDatesDecidedDates" BLOB, "offestDatesConfirmedCancelled" BLOB, "slDatesConfirmedCancelled" BLOB, "vlDatesConfirmedCancelled" BLOB, proposed_offset INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY("userId") REFERENCES users (id)
);
CREATE TABLE users (
	id INTEGER NOT NULL, 
	first_name VARCHAR(50) NOT NULL, 
	middle_name VARCHAR(50) NOT NULL, 
	last_name VARCHAR(50) NOT NULL, 
	email VARCHAR(255) NOT NULL, 
	username VARCHAR(50) NOT NULL, 
	password VARCHAR(255) NOT NULL, 
	active_role VARCHAR(255), is_supervisor VARCHAR(255), supervisee VARCHAR(255), supervisor VARCHAR(255), 
	PRIMARY KEY (id), 
	UNIQUE (email), 
	UNIQUE (username)
);
INSERT INTO `users` VALUES (1,'Seer','admin','Administrator','seeradmin@seer.com','seer','pbkdf2:sha1:1000$owLeMbAR$5212fad369e96502490c780c708f6b3c3e661ef0','Administrator','1',' darknessinzero Liyah',NULL);
CREATE TABLE user_roles (
	user_id INTEGER NOT NULL, 
	role_id INTEGER NOT NULL, 
	PRIMARY KEY (user_id, role_id), 
	FOREIGN KEY(role_id) REFERENCES roles (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
INSERT INTO `user_roles` VALUES (1,1);
CREATE TABLE user_projects (
	id INTEGER NOT NULL, 
	user_id INTEGER, 
	project_id INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(project_id) REFERENCES projects (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE roles (
	id INTEGER NOT NULL, 
	name VARCHAR(64), 
	PRIMARY KEY (id), 
	UNIQUE (name)
);
INSERT INTO `roles` VALUES (1,'Administrator');
CREATE TABLE role_perms (
	role_id INTEGER NOT NULL, 
	permission_id INTEGER NOT NULL, 
	PRIMARY KEY (role_id, permission_id), 
	FOREIGN KEY(permission_id) REFERENCES permissions (id), 
	FOREIGN KEY(role_id) REFERENCES roles (id)
);
INSERT INTO `role_perms` VALUES (1,1);
INSERT INTO `role_perms` VALUES (1,2);
INSERT INTO `role_perms` VALUES (1,3);
INSERT INTO `role_perms` VALUES (1,4);
INSERT INTO `role_perms` VALUES (1,5);
CREATE TABLE projects (
	id INTEGER NOT NULL, 
	project_name VARCHAR(50), 
	description TEXT, 
	PRIMARY KEY (id), 
	UNIQUE (project_name)
);
CREATE TABLE "profileImages" (
	id INTEGER NOT NULL, 
	user_id INTEGER, 
	is_active INTEGER, 
	image VARCHAR(200), 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id)
);
CREATE TABLE permissions (
	id INTEGER NOT NULL, 
	permission_name VARCHAR(50) NOT NULL, 
	PRIMARY KEY (id), 
	UNIQUE (permission_name)
);
INSERT INTO `permissions` VALUES (1,'Administrator');
INSERT INTO `permissions` VALUES (2,'View Payslip');
INSERT INTO `permissions` VALUES (3,'HR Functionalities');
INSERT INTO `permissions` VALUES (4,'See Projects');
INSERT INTO `permissions` VALUES (5,'Upload Payslip');
CREATE TABLE logs (
	id INTEGER NOT NULL, 
	user_id INTEGER, 
	date DATETIME, 
	description TEXT, 
	hours FLOAT NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id), 
	UNIQUE (hours)
);
CREATE TABLE alembic_version (
	version_num VARCHAR(32) NOT NULL
);
INSERT INTO `alembic_version` VALUES ('3d91a2a86b6f');
CREATE TABLE "Payslip" (
	id INTEGER NOT NULL, 
	description TEXT, 
	date DATETIME, 
	user INTEGER, 
	filename VARCHAR(64), 
	PRIMARY KEY (id), 
	FOREIGN KEY(user) REFERENCES users (id)
);
CREATE INDEX "ix_Payslip_date" ON "Payslip" (date);
COMMIT;
