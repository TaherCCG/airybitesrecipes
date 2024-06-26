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

});