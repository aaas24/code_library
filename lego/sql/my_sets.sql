CREATE TABLE IF NOT EXISTS my_sets (
    model_id INTEGER,
    type TEXT,
    set_num TEXT,
    set_name TEXT,
    pieces INTEGER,
    age INTEGER,
    year INTEGER,
    theme TEXT,
    instructions_link TEXT,
    photo_link TEXT,
    quantity INTEGER,
    on_display BOOLEAN,
    last_updated TIMESTAMP
);
