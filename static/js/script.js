$(document).ready(function () {
    // Initialise Materialize components
    // SideNaV
    $('.sidenav').sidenav();
    // Collapsible
    $('.collapsible').collapsible();
    // Select option
    $('select').formSelect();

    /* 
    Refrences for my workout to add ingredient input fields dynamically
    ref 1: https://www.mongodb.com/community/forums/t/how-to-and-a-new-field-and-update-value-dynamically-through-mongo-shell/266383
    ref 2: https://stackoverflow.com/questions/53083602/dynamically-populating-a-field-with-addfields-when-getting-document-by-id  
    */
    
    // Function to add ingredient input fields dynamically.
    let ingredientCount = 1;

    function addIngredient() {
        ingredientCount++;
        const ingredientsDiv = document.getElementById('ingredients');
        const newIngredientDiv = document.createElement('div');
        newIngredientDiv.classList.add('row', 'ingredient');
        newIngredientDiv.innerHTML = `
            <div class="input-field col s6">
                <label for="ingredient_name_${ingredientCount}">Ingredient Name</label>
                <input type="text" id="ingredient_name_${ingredientCount}" name="ingredient_name[]" class="validate" required>
            </div>
            <div class="input-field col s6">
                <label for="ingredient_quantity_${ingredientCount}">Quantity</label>
                <input type="text" id="ingredient_quantity_${ingredientCount}" name="ingredient_quantity[]" class="validate" required>
            </div>
        `;
        ingredientsDiv.appendChild(newIngredientDiv);
    }

    // Event listener for "Add Another Ingredient" button
    $('#add-ingredient-btn').on('click', function () {
        addIngredient();
    });

    // Validate Naterialize Category Selector
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

});