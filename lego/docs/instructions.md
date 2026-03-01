Background :
I have multiple sets of lego and I would like to see what other sets I could build with the existing pieces

LANGUAGES
- pyton
- sql

SERVICES OR COMPONENTS
- Brickable: 
This includes the documentation with the database of artifacts that can be downloaded by using a url construction with the file name. Ex. for themes, we would use: https://cdn.rebrickable.com/media/downloads/themes.csv.zip

It also includes an aPI to query models. 

- User Interface (UI)
The program should have a basic UI built using python. The user interface will allow to trigger a search based on the current state of the tables. It's main purpose is to:

1. Report in a single view information on the models that can be build using the existing inventory. 

2. Trigger a search on Brickable API


- Database (SQL)
Preference on duckdb but open for recommendations. Porposed schema:

my_sets(
  model_id,
  type (set | moc),
  on_display (True | False),
  parts_required[],
  last_updated
)
favorite_themes(
    themes
)
sets (
  set_num,
  name,
  owned_percentage,
  theme
  in_favorite (True | False)
  count_group (<500 |  1000-1500 |  >1500 pieces)
  difficulty (Kid friendly, adult)
  photo 
)
models (
  model_id,
  type (set | moc),
  parts_required[],
  
)
colors()
part_categories ()
parts (
  part_num,
  color_id,
  quantity
)
part_relationships()
elements()
minifigs()
inventories()
inventory_parts()
inventory_sets()
inventory_minifigs()

PROGRAM FLOW

1. Create a SQL database on my inventory
1.1 Create or replace table with my sets  (my_sets). This table should have a column for 'on_display' marked as True or false. When true, this column implies that the set is not meant to be used as part of a new build because is currently on display. Everytime a change is done to this table, the program should update the calculations on the missing pieces to models we have stored their information locally. 

1.2 Use Brickable tables to calculate the full inventory based on sets listed in my_sets

1.3 Create or replace table with favorite_themes: this table with habe themes that I like to have the most, including:

- Harry Potter
- Deco
- Technic
- Love
- Nintendo, Mario, Yoshi 
- Star Wars
- Architecture
- Art
- Botanicals, plants


2. Create an inventory of models

Because Brickable does not expose the “Given my inventory, return matching builds”, we need to find a way to decide which models we can pull. However, due to API limitations, we shoudl store the information returned and make the model suggest the existing first. To do this, we should have locally the following information of models 

- Set/model name
- pieces count
- theme
- difficulty, this can be based on pieces count to help separate kid friendly sets
- Photo of set taken from internet
- instructions available (Y/N)
- Percentage of identify missing piece (The higher the better)

To help populate this database, we need to: 

2.1 Download existing lego inventory (lego_inventory) using Brickable documentation into models table, including: 

- themes: https://cdn.rebrickable.com/media/downloads/themes.csv.zip
- colors: 
- part_categories
- parts
- part_relationships
- elements
- sets
- minifigs
- inventories
- inventory_parts
- inventory_sets
- inventory_minifigs

2.2 Enrich inventory list of sets with:  
- Theme
- If theme in favorite_theme list (True/False)
- Total count pieces
- Count grouping (<500, 1000-1500, >1500 pieces)
- Difficulty: Kid friendly or not. Criteria on this dimension shuld be defined later
- Photo of set taken from internet and stored locally


3. Decide Candidate models

The model should calculate the percentage of pieces we have in the inventory vs each model in the lego_inventory table. This calculation should be done only if a significant change was done to the 'my_sets' table, meaning, only if it was last updated. This will avoid reprocesing. 

A search on the existing Lego_inventory and confirm we have minimum 10 models that match the following criteria. Results should be ranked by 
- 85% or more of pieces are existing (must)
- Do the models belong to one of the themes in favorite_themes table

4. Report to user in UI
The user interface (UI) will allow to trigger a search based on the current state of the tables. It's main purpose is to:

1. Report in a single view information on the models that can be build using the existing inventory. This view shoudl include name, images, when available, the total count of pieces, theme, estimated % covered with existing pieces. 

2. Trigger a serach on Brickable API
If the proposed set of models is found wanted by the user, meaning it did not file a model to build, the UI should allow the user to trigger a search on the API and report back those new models as additional options to the ones it recommended. Before doing the search, the user should be able to adjust some of the filters to identify candidate models, including:

- If build is kid friendly
- Adjust favorite themes list


5. Explore other sets using brickable API

If the step before does not render 10 models or the user decides to trigger a serach none the less, the program should connect to the API requesting candidate models and store information locally. These should include: 
	•	“Builds you can make”
    •	MOCs (fan-designed builds)
	•	Official alternate builds

We will define the querying the API later. 

The program should cache the parts list and calculate % of existing parts:
for part in model.parts:
  if owned_qty < required_qty:
    deficit += required_qty - owned_qty

If the deficit is <15%, the program should show store the information into the model table and enrich the result. 