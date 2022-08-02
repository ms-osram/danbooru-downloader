CREATE TABLE post(
	id 
	INTEGER
	PRIMARY KEY,
	rating 
	TEXT
	NOT NULL,
	image_width 
	INTEGER
	NOT NULL,
	image_height 
	INTEGER
	NOT NULL
	) strict;
	
CREATE TABLE tag(
	id 
	INTEGER
	PRIMARY KEY,
	name 
	TEXT
	NOT NULL,
	category 
	INTEGER
	NOT NULL
	) strict;
	
CREATE TABLE post_tags(
	post_id 
	INTEGER
	NOT NULL
	REFERENCES post(id),
	tag_id 
	INTEGER
	NOT NULL
	REFERENCES tag(id),
	
	UNIQUE (post_id, tag_id) ON conflict IGNORE
	) strict;
	
	
	
	