    // on cache les propriétés suivant les catégories choisies
    function is_numero_visible() {
    let e = document.getElementById("id_utiliser_suivant");
    return !(e.checked);
}
function is_biblio() {
    for (let i = 1; i <= 3; i++) {
    let e = document.querySelectorAll("#id_categorie" + i + " option:checked")[0].getAttribute("value");
    if (document.categories_bibio.includes(e))
        return true;
    }

    return false;
}
function is_site() {
    for (let i = 1; i <= 3; i++) {
    let e = document.querySelectorAll("#id_categorie" + i + " option:checked")[0].getAttribute("value");
    if (document.categories_site.includes(e))
        return true;
    }

    return false;
}
function is_film() {
    for (let i = 1; i <= 3; i++) {
    let e = document.querySelectorAll("#id_categorie" + i + " option:checked")[0].getAttribute("value");
    if (document.categories_film.includes(e))
        return true;
    }

    return false;
}

function set_visible(list_fields, visible) {
    list_fields.forEach(function(item, index, array) {
    field = "field_wrapper_id_" + item;
    var els = document.getElementById(field);
        if (visible)
            els.style.display = 'flex';
        else
            els.style.display = 'none';
    });
}

function set_enable(list_fields, enable) {
    list_fields.forEach(function(item, index, array) {
    var els = document.getElementById(item);
        if (enable)
        els.style.visibility = "visible";
        else
        els.style.visibility = "hidden";
    });
}

function update_visible_fields() {        
    let biblio_fields = ["titre", "auteurs", "annee_publication", "editeur", "format_bibl", "quatrieme_de_couverture", "collection"];
    let film_fields = ["realisateurs", "annee_film", "diffusion", "duree", "production"];
    let site_fields = ["plan_du_site"];
    set_visible(biblio_fields, is_biblio());
    set_visible(site_fields, is_site());
    set_visible(film_fields, is_film());

    let numero_fields = ["id_numero"];
    set_enable(numero_fields, is_numero_visible());
}

for (let i = 1; i <= 3; i++) {
    let selectElement = document.getElementById("id_categorie" + i);

    selectElement.addEventListener('change', (event) => {
    update_visible_fields();
    });

}
let selectElement = document.getElementById("id_utiliser_suivant");
selectElement.addEventListener('change', (event) => {
    update_visible_fields();
});

function ready(callback){
    // in case the document is already rendered
    if (document.readyState!='loading') callback();
    // modern browsers
    else if (document.addEventListener) document.addEventListener('DOMContentLoaded', callback);
    // IE <= 8
    else document.attachEvent('onreadystatechange', function(){
        if (document.readyState=='complete') callback();
    });
}

ready(function(){
    update_visible_fields();
});


