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


@app.errorhandler(404)
def page_not_found(e):
    """404 Page"""
    return render_template('404.html'), 404


@app.before_request
def before_request():
    """Check user role before each request."""
    g.user_role = None
    if 'user' in session:
        user = mongo.db.users.find_one({"username": session['user']})
        if user:
            g.user_role = user.get('role', 'user')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        """Decorator to check if the user is logged in."""
        if 'user' not in session:
            flash("You need to be logged in to access this page.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def check_role(*args, **kwargs):
        """Decorated function to check if user is admin or not."""
        if 'user' not in session:
            flash("You need to be logged in to access this page.", "error")
            return redirect(url_for("login"))
        user = mongo.db.users.find_one({"username": session['user']})
        if not user or user.get('role') != 'admin':
            flash(
                    f"""You do not have the necessary permissions
                        to access this page.""", "error")
            return redirect(url_for("get_recipes"))
        return f(*args, **kwargs)
    return check_role


@app.route("/")
@app.route("/get_recipes")
def get_recipes():
    """Route to display recipes."""
    recipes = mongo.db.recipes.find()
    return render_template(
        "index.html", recipes=recipes,
        get_ingredient_name=get_ingredient_name)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Route to display registration page."""
    if request.method == "POST":
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # Check if password match
        if password != confirm_password:
            flash("Passwords do not match. Please try again.", "warning")
            return redirect(url_for("register"))

        # Check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash(
                    f"""Username already exists.
                        Please choose another username.""", "warning")
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


@app.route('/admin_panel')
@admin_required
def admin_panel():
    """Route to admin panel."""
    users = mongo.db.users.find()
    return render_template('admin_panel.html', users=users)


@app.route('/admin/user_roles')
@admin_required
def user_roles():
    """Add a route to render the user_roles page."""
    users = mongo.db.users.find()
    return render_template('user_roles.html', users=users)


@app.route('/update_role/<user_id>', methods=['POST'])
@admin_required
def update_role(user_id):
    """Add a route to render the user_roles page."""
    new_role = request.form['role']
    mongo.db.users.update_one({
        "_id": ObjectId(user_id)},
        {"$set": {"role": new_role}})
    flash("User role updated.", "success")
    return redirect(url_for('user_roles'))


@app.route("/delete_user/<user_id>", methods=["POST"])
@admin_required
def delete_user(user_id):
    """Delete User"""
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


@app.route("/login", methods=["GET", "POST"])
def login():
    """Route to display login page."""
    if request.method == "POST":
        # Check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # Check if hashed password of user matches
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(request.form.get("username")),
                      "success")
                return redirect(url_for("profile", username=session["user"]))
            else:
                # Password not match to user message
                flash(
                        f"""Incorrect Username and/or Password!
                            Please check and try again.""", "warning")
                return redirect(url_for("login"))

        else:
            # User does not exist
            flash(
                    f"""Incorrect Username and/or Password!
                        Please check and try again.""", "warning")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
@login_required
def profile(username):
    """Route to display user profile page."""
    # Get username session username from the database
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]
    # Fetch the user's recipes from the database
    recipes = list(mongo.db.recipes.find({"created_by": username}))
    return render_template("profile.html", username=username, recipes=recipes)


@app.route("/logout")
@login_required
def logout():
    """Route to remove user from session."""
    # Remove user session (logout)
    flash("You have logged out", "success")
    session.pop("user")
    return redirect(url_for("get_recipes"))


# Ref 1: https://flask-pymongo.readthedocs.io/en/latest/

def get_ingredient_name(ingredient_id):
    """Helper function to get ingredient name by id."""
    ingredient = mongo.db.ingredients.find_one({
        "_id": ObjectId(ingredient_id)})
    if ingredient:
        return ingredient["ing_name"]
    return "Unknown Ingredient"

# Below I registered the get_ingredient_name function as a global function
# This allows the function to be called directly within any Jinja2 template
# without needing to pass it explicitly.
# Ref1: https://flask.palletsprojects.com/en/2.3.x/templating/
# Ref2:
# https://stackoverflow.com/questions/43335931/global-variables-in-flask-templates


app.jinja_env.globals.update(get_ingredient_name=get_ingredient_name)


@app.route("/add_recipe", methods=["GET", "POST"])
@login_required
def add_recipe():
    """Route to add recipe to the database."""
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
        tags = request.form["tags"].split(",")

        ingredient_names = request.form.getlist("ingredient_name[]")
        ingredient_quantities = request.form.getlist("ingredient_quantity[]")

        ingredient_refs = []

        for name, quantity in zip(ingredient_names, ingredient_quantities):
            ingredient = mongo.db.ingredients.find_one({"ing_name": name})
            if not ingredient:
                ingredient_id = mongo.db.ingredients.insert_one({
                    "ing_name": name}).inserted_id
            else:
                ingredient_id = ingredient["_id"]
            ingredient_refs.append({
                "ingredient_id": ingredient_id,
                "quantity": quantity
            })

        created_at = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        updated_at = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

        recipe = {
            "recipe_title": recipe_title,
            "recipe_description": recipe_description,
            "instructions": instructions,
            "cook_time": cook_time,
            "prep_time": prep_time,
            "total_time": total_time,
            "temperature": temperature,
            "servings": servings,
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


@app.route("/edit_recipe/<recipe_id>", methods=["GET", "POST"])
@login_required
def edit_recipe(recipe_id):
    """ Edit / Update recipe."""
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
        tags = request.form["tags"].split(",")

        ingredient_names = request.form.getlist("ingredient_name[]")
        ingredient_quantities = request.form.getlist("ingredient_quantity[]")

        ingredient_refs = []

        for name, quantity in zip(ingredient_names, ingredient_quantities):
            ingredient = mongo.db.ingredients.find_one({"ing_name": name})
            if not ingredient:
                ingredient_id = mongo.db.ingredients.insert_one({
                    "ing_name": name}).inserted_id
            else:
                ingredient_id = ingredient["_id"]
            ingredient_refs.append({
                "ingredient_id": ingredient_id,
                "quantity": quantity
            })

        updated_at = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

        update = {
            "recipe_title": recipe_title,
            "recipe_description": recipe_description,
            "instructions": instructions,
            "cook_time": cook_time,
            "prep_time": prep_time,
            "total_time": total_time,
            "temperature": temperature,
            "servings": servings,
            "category": category,
            "tags": tags,
            "ingredients": ingredient_refs,
            "updated_at": updated_at,
        }

        mongo.db.recipes.update_one({
            "_id": ObjectId(recipe_id)},
            {"$set": update})
        flash("Recipe Successfully Updated", "success")
        # Redirect to manage_recipes.html after updating the recipe
        return redirect(url_for("manage_recipes"))

    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipe_id)})
    categories = mongo.db.categories.find().sort("category_name", 1)
    return render_template(
        "edit_recipe.html", recipe=recipe, categories=categories)


@app.route("/delete_recipe/<recipe_id>", methods=["POST"])
@login_required
def delete_recipe(recipe_id):
    """Delete Recipe."""
    mongo.db.recipes.delete_one({"_id": ObjectId(recipe_id)})
    flash("Recipe Successfully Deleted", "success")
    return redirect(url_for("get_recipes"))


@app.route("/get_categories")
@admin_required
def get_categories():
    """Route to get categories."""
    categories = list(mongo.db.categories.find().sort("category_name", 1))

    # Iterate categories and add recipe count
    for category in categories:
        recipe_count = mongo.db.recipes.count_documents({
            "category": category['category_name']})
        category['recipe_count'] = recipe_count

    return render_template("categories.html", categories=categories)


@app.route("/add_category", methods=["POST"])
@admin_required
def add_category():
    """Route ta add a Category."""
    if request.method == "POST":
        category_name = request.form.get("category_name")
        if category_name:
            existing_category = mongo.db.categories.find_one({
                "category_name": category_name})
            if existing_category:
                flash(f"Category '{category_name}' already exists.", "warning")
            else:
                mongo.db.categories.insert_one({
                    "category_name": category_name})
                flash(
                    f"Category '{category_name}' added successfully.",
                    "success")
        else:
            flash("Category name is required.", "error")
            return redirect(url_for("get_categories"))

    return redirect(url_for("get_categories"))


@app.route("/edit_category", methods=["POST"])
@admin_required
def edit_category():
    """Route to edit category."""
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


@app.route("/delete_category", methods=["POST"])
@admin_required
def delete_category():
    """Route to delete category."""
    category_id = request.form.get("category_id")
    if category_id:
        mongo.db.categories.delete_one({"_id": ObjectId(category_id)})
        flash("Category deleted successfully.", "success")
    else:
        flash("Category ID is required.", "error")
    return redirect(url_for("get_categories"))


@app.route("/manage_recipes")
@login_required
def manage_recipes():
    """Route to manage"""
    user = mongo.db.users.find_one({"username": session['user']})
    if not user or user.get('role') != 'admin':
        return redirect(url_for("get_recipes"))

    recipes = list(mongo.db.recipes.find())
    return render_template("manage_recipes.html", recipes=recipes)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
