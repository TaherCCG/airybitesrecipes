import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for, g)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from functools import wraps
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

# Check user role before each request
@app.before_request
def before_request():
    g.user_role = None
    if 'user' in session:
        user = mongo.db.users.find_one({"username": session['user']})
        if user:
            g.user_role = user.get('role', 'user')


# Decorator to check if the user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash("You need to be logged in to access this page.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# Decorated function to check if user is admin or not
def admin_required(f):
    @wraps(f)
    def check_role(*args, **kwargs):
        if 'user' not in session:
            flash("You need to be logged in to access this page.", "error")
            return redirect(url_for("login"))
        user = mongo.db.users.find_one({"username": session['user']})
        if not user or user.get('role') != 'admin':
            flash("You do not have the necessary permissions to access this page.", "error")
            return redirect(url_for("get_recipes"))
        return f(*args, **kwargs)
    return check_role


# Route to display recipes
@app.route("/")
@app.route("/get_recipes")
def get_recipes():
    recipes = mongo.db.recipes.find()
    return render_template("index.html", recipes=recipes, get_ingredient_name=get_ingredient_name)


# Route to display registration page
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Check if password match
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            flash("Passwords do not match. Please try again.", "warning")
            return redirect(url_for("register"))

        # Check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists.<br>Please choose another username.", "warning")
            return redirect(url_for("register"))

        # Set default role to user
        role = "user"

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "role": role
        }
        mongo.db.users.insert_one(register)

        # Put new User into Session (cookie)
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!", "success")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("register.html")


# Route to admin panel
@app.route('/admin_panel')
@admin_required
def admin_panel():
    users = mongo.db.users.find()
    return render_template('admin_panel.html', users=users)


# Add a route to render the user_roles page
@app.route('/admin/user_roles')
@admin_required
def user_roles():
    users = mongo.db.users.find()
    return render_template('user_roles.html', users=users)

# Update User Role
@app.route('/update_role/<user_id>', methods=['POST'])
@admin_required
def update_role(user_id):
    new_role = request.form['role']
    mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"role": new_role}})
    flash("User role updated.", "success")
    return redirect(url_for('user_roles'))

# Delete User
@app.route("/delete_user/<user_id>", methods=["POST"])
@admin_required
def delete_user(user_id):
    delete_recipes = request.form.get('delete_recipes') == 'true'
    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    
    if user:
        mongo.db.users.delete_one({"_id": ObjectId(user_id)})
        
        if delete_recipes:
            mongo.db.recipes.delete_many({"created_by": user["username"]})
        
        if delete_recipes:
            flash("User and their recipes successfully deleted", "success")
        else:
            flash("User successfully deleted", "success")
    else:
        flash("User not found.", "error")
    
    return redirect(url_for("user_roles"))


# Route to display login page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
         # Check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # Check if hashed password of user matches
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")),"success")
                return redirect(url_for("profile", username=session["user"]))
            else:
                # Password not match to user message
                flash("Incorrect Username and/or Password! Please check and try again.", "warning")
                return redirect(url_for("login"))

        else:
            # User does not exist
            flash("Incorrect Username and/or Password! Please check and try again.", "warning")
            return redirect(url_for("login"))

    return render_template("login.html")


# Route to display user profile page
@app.route("/profile/<username>", methods=["GET", "POST"])
@login_required
def profile(username):
    # Get username session username from the database
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
     # Fetch the user's recipes from the database
    recipes = list(mongo.db.recipes.find({"created_by": username}))
    return render_template("profile.html", username=username, recipes=recipes)


# Route to remove user from session 
@app.route("/logout")
@login_required
def logout():
    # Remove user session (logout)
    flash("You have logged out","success")
    session.pop("user")
    return redirect(url_for("get_recipes"))


# Ref 1: https://flask-pymongo.readthedocs.io/en/latest/
# Helper function to get ingredient name by id
def get_ingredient_name(ingredient_id):
    ingredient = mongo.db.ingredients.find_one({"_id": ObjectId(ingredient_id)})
    if ingredient:
        return ingredient["ing_name"]
    return "Unknown Ingredient"

# Below I registered the get_ingredient_name function as a global function in Jinja2 templates
# This allows the function to be called directly within any Jinja2 template without
# needing to pass it explicitly.
# Ref1: https://flask.palletsprojects.com/en/2.3.x/templating/
# Ref2: https://stackoverflow.com/questions/43335931/global-variables-in-flask-templates
app.jinja_env.globals.update(get_ingredient_name=get_ingredient_name)


# Route to add recipe to the database
@app.route("/add_recipe", methods=["GET", "POST"])
@login_required
def add_recipe():
    if request.method == "POST":
        category = request.form["category_name"]
        recipe_title = request.form["recipe_title"]
        recipe_description = request.form["recipe_description"]
        cook_time = int(request.form["cook_time"])
        prep_time = int(request.form["prep_time"])
        total_time = cook_time + prep_time
        temperature = int(request.form["temperature"])
        servings = int(request.form["servings"])
        instructions = request.form["instructions"].split("\n")
        image_url = request.form["image_url"]
        tags = request.form["tags"].split(",")

        ingredient_names = request.form.getlist("ingredient_name[]")
        ingredient_quantities = request.form.getlist("ingredient_quantity[]")

        ingredient_refs = []

        for name, quantity in zip(ingredient_names, ingredient_quantities):
            ingredient = mongo.db.ingredients.find_one({"ing_name": name})  # Use "ing_name" here
            if not ingredient:
                ingredient_id = mongo.db.ingredients.insert_one({"ing_name": name}).inserted_id  # Insert new ingredient
            else:
                ingredient_id = ingredient["_id"]
            ingredient_refs.append({
                "ingredient_id": ingredient_id,
                "quantity": quantity
            })

        created_at = datetime.datetime.now()
        updated_at = datetime.datetime.now()

        recipe = {
            "recipe_title": recipe_title,
            "recipe_description": recipe_description,
            "instructions": instructions,
            "cook_time": cook_time,
            "prep_time": prep_time,
            "total_time": total_time,
            "temperature": temperature,
            "servings": servings,
            "image_url": image_url,
            "category": category,
            "tags": tags,
            "ingredients": ingredient_refs,
            "created_at": created_at,
            "updated_at": updated_at,
            "created_by": session["user"]
        }
        mongo.db.recipes.insert_one(recipe)
        flash("Recipe Successfully Added", "success")
        return redirect(url_for("get_recipes"))

    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("add_recipe.html", categories=categories)


# Edit / Update recipe  
@app.route("/edit_recipe/<recipe_id>", methods=["GET", "POST"])
@login_required
def edit_recipe(recipe_id):
    if request.method == "POST":
        category = request.form["category_name"]
        recipe_title = request.form["recipe_title"]
        recipe_description = request.form["recipe_description"]
        cook_time = int(request.form["cook_time"])
        prep_time = int(request.form["prep_time"])
        total_time = cook_time + prep_time
        temperature = int(request.form["temperature"])
        servings = int(request.form["servings"])
        instructions = request.form["instructions"].split("\n")
        image_url = request.form["image_url"]
        tags = request.form["tags"].split(",")

        ingredient_names = request.form.getlist("ingredient_name[]")
        ingredient_quantities = request.form.getlist("ingredient_quantity[]")

        ingredient_refs = []

        for name, quantity in zip(ingredient_names, ingredient_quantities):
            ingredient = mongo.db.ingredients.find_one({"ing_name": name}) 
            if not ingredient:
                ingredient_id = mongo.db.ingredients.insert_one({"ing_name": name}).inserted_id  # Insert new ingredient
            else:
                ingredient_id = ingredient["_id"]
            ingredient_refs.append({
                "ingredient_id": ingredient_id,
                "quantity": quantity
            })

        created_at = datetime.datetime.now()
        updated_at = datetime.datetime.now()

        update = {
            "recipe_title": recipe_title,
            "recipe_description": recipe_description,
            "instructions": instructions,
            "cook_time": cook_time,
            "prep_time": prep_time,
            "total_time": total_time,
            "temperature": temperature,
            "servings": servings,
            "image_url": image_url,
            "category": category,
            "tags": tags,
            "ingredients": ingredient_refs,
            "created_at": created_at,
            "updated_at": updated_at,
            "created_by": session["user"]
        }

        mongo.db.recipes.update_one({"_id": ObjectId(recipe_id)}, {"$set": update})
        flash("Recipe Successfully Updated", "success")
        return redirect(url_for("get_recipes"))

    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template("edit_recipe.html", recipe=recipe, categories=categories)

# Delete Recipe
@app.route("/delete_recipe/<recipe_id>", methods=["POST"])
@login_required
def delete_recipe(recipe_id):
    mongo.db.recipes.delete_one({"_id": ObjectId(recipe_id)})
    flash("Recipe Successfully Deleted", "success")
    return redirect(url_for("get_recipes"))


@app.route("/get_categories")
@admin_required
def get_categories():
    categories = list(mongo.db.categories.find().sort("category_name", 1))
    
    # Iterate categories and add recipe count
    for category in categories:
        recipe_count = mongo.db.recipes.count_documents({"category": category['category_name']})
        category['recipe_count'] = recipe_count
    
    return render_template("categories.html", categories=categories)


# Route to Add Category
@app.route("/add_category", methods=["POST"])
@admin_required
def add_category():
    if request.method == "POST":
        category_name = request.form.get("category_name")
        if category_name:
            existing_category = mongo.db.categories.find_one({"category_name": category_name})
            if existing_category:
                flash(f"Category '{category_name}' already exists.", "warning")
            else:
                mongo.db.categories.insert_one({"category_name": category_name})
                flash(f"Category '{category_name}' added successfully.", "success")
        else:
            flash("Category name is required.", "error")
            return redirect(url_for("get_categories")) 
    
    return redirect(url_for("get_categories"))


# Route to edit category 
@app.route("/edit_category", methods=["POST"])
@admin_required
def edit_category():
    category_id = request.form.get("category_id")
    category_name = request.form.get("category_name")
    if category_id and category_name:
        mongo.db.categories.update_one(
            {"_id": ObjectId(category_id)},
            {"$set": {"category_name": category_name}}
        )
        flash("Category updated successfully.", "success")
    else:
        flash("Category name is required.", "error")
    return redirect(url_for("get_categories"))    


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"), port=int(os.environ.get("PORT")), debug=True)
