$(document).ready(function () {
    // Initialise Materialize components
    // SideNaV
    $('.sidenav').sidenav();
    // Collapsible
    $('.collapsible').collapsible();
    // Select option
    $('select').formSelect();
    // Modal
    $('.modal').modal();

    /* 
    Refrences for my workout to add ingredient input fields dynamically
    ref 1: https://www.mongodb.com/community/forums/t/how-to-and-a-new-field-and-update-value-dynamically-through-mongo-shell/266383
    ref 2: https://stackoverflow.com/questions/53083602/dynamically-populating-a-field-with-addfields-when-getting-document-by-id  
    */

    let ingredientCount = 1;

    // Function to add ingredient input fields dynamically.
    function addIngredient() {
        ingredientCount++;
        const ingredientsDiv = document.getElementById('ingredients');
        const newIngredientDiv = document.createElement('div');
        newIngredientDiv.classList.add('row', 'ingredient');
        newIngredientDiv.innerHTML = `
        <div class="input-field col s5">
            <label for="ingredient_name_${ingredientCount}">Ingredient Name</label>
            <input type="text" id="ingredient_name_${ingredientCount}" name="ingredient_name[]" class="validate" required>
        </div>
        <div class="input-field col s5">
            <label for="ingredient_quantity_${ingredientCount}">Quantity</label>
            <input type="text" id="ingredient_quantity_${ingredientCount}" name="ingredient_quantity[]" class="validate" required>
        </div>
        <div class="input-field col s2" style="display: flex; align-items: center;">
            <button type="button" class="btn remove-ingredient-btn">X</button>
        </div>
    `;
        ingredientsDiv.appendChild(newIngredientDiv);
    }

    // Event listener for dynamically added remove buttons
    document.addEventListener('click', function (event) {
        if (event.target.classList.contains('remove-ingredient-btn')) {
            const button = event.target;
            const ingredientDiv = button.parentElement.parentElement;
            ingredientDiv.remove();
        }
    });

    // Event listener for "Add Another Ingredient" button
    document.getElementById('add-ingredient-btn').addEventListener('click', function () {
        addIngredient();
    });

    validateMaterializeSelect();
    function validateMaterializeSelect() {
        let classValid = { "border-bottom": "1px solid #4caf50", "box-shadow": "0 1px 0 0 #4caf50" };
        let classInvalid = { "border-bottom": "1px solid #f44336", "box-shadow": "0 1px 0 0 #f44336" };
        if ($("select.validate").prop("required")) {
            $("select.validate").css({ "display": "block", "height": "0", "padding": "0", "width": "0", "position": "absolute" });
        }
        $(".select-wrapper input.select-dropdown").on("focusin", function () {
            $(this).parent(".select-wrapper").on("change", function () {
                if ($(this).children("ul").children("li.selected:not(.disabled)").on("click", function () { })) {
                    $(this).children("input").css(classValid);
                }
            });
        }).on("click", function () {
            if ($(this).parent(".select-wrapper").children("ul").children("li.selected:not(.disabled)").css("background-color") === "rgba(0, 0, 0, 0.03)") {
                $(this).parent(".select-wrapper").children("input").css(classValid);
            } else {
                $(".select-wrapper input.select-dropdown").on("focusout", function () {
                    if ($(this).parent(".select-wrapper").children("select").prop("required")) {
                        if ($(this).css("border-bottom") != "1px solid rgb(76, 175, 80)") {
                            $(this).parent(".select-wrapper").children("input").css(classInvalid);
                        }
                    }
                });
            }
        });
    }

    let userIdToDelete = '';

    window.showDeleteModal = function (userId) {
        userIdToDelete = userId;
        const modal = document.getElementById('deleteUserModal');
        const instance = M.Modal.getInstance(modal);
        instance.open();
    }

    window.confirmDelete = function () {
        const deleteRecipes = document.getElementById('deleteRecipesCheckbox').checked;
        document.getElementById('deleteRecipesInput').value = deleteRecipes ? 'true' : 'false';
        const form = document.getElementById('deleteUserForm');
        form.action = `/delete_user/${userIdToDelete}`;
        form.submit();

        const modal = document.getElementById('deleteUserModal');
        const instance = M.Modal.getInstance(modal);
        instance.close();
    }
});