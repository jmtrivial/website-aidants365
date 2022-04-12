var modal = $('#popup_add_dynamique');

function show_add_dynamique(node, select2) {
    select2.select2("close");
    modal.css("display", "block");
    clearErreur();
    if (node.prev().attr("id") == "select2-id_categories_libres_m2m-results") {
        titre = "une catégorie libre";
        document.classe_popup = "categorie_libre";
        document.select_popup = "#id_categories_libres_m2m";
    }
    else if (node.prev().attr("id") == "select2-id_themes_m2m-results") {
        titre = "un thème";
        document.classe_popup = "theme";
        document.select_popup = "#id_themes_m2m";
    }
    else if (node.prev().attr("id") == "select2-id_mots_cles_m2m-results") {
        titre = "un mot-clé";
        document.classe_popup = "motcle";
        document.select_popup = "#id_mots_cles_m2m";
    }
    else if (node.prev().attr("id") == "select2-id_motscles_m2m-results") {
        titre = "un mot-clé";
        document.classe_popup = "motcle";
        document.select_popup = "#id_motscles_m2m";
    }

    modal.find(".popup_head span").html(titre);
    $("#popup_name").val(document.popup_preval);
}

var annuler = document.getElementsByClassName("annuler_popup")[0];

annuler.onclick = function() {
    modal.css("display", "none");
}

var ajouter = document.getElementsByClassName("ajouter_popup")[0];

function setErreur(msg) {
    $(".erreur_popup").html(msg);
    $(".erreur_popup").css("display", "block");
}

function clearErreur() {
    $(".erreur_popup").css("display", "none");
}


ajouter.onclick = function() {
    const headers = {
        'X-CSRFToken': window.csrftoken
      };

    const url = "/fichier/" + document.classe_popup + "/api/";

    $.ajax({
        type: "POST",
        headers,
        url: url,
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        data: JSON.stringify({nom: $("#popup_name").val()}),
        success: function (data) {
            if ("error" in data) {
                setErreur(data["error"]);
            }
            else if (!(("nom" in data) && ("id" in data))) {
                setErreur("Une erreur s'est produite pendant l'enregistrement. Veuillez essayer plus tard.");
            }
            else {
                nom = data["nom"];
                id = data["id"];
                nouvelle_entree = new Option(nom, id, true, true); // '<option value="' + id + '">' + nom + '</option>';
                $(document.select_popup).append(nouvelle_entree);
                $(document.select_popup).trigger('change');
                modal.css("display", "none");
            }
        },
        error: function(xhr, status, error) {
            setErreur("Erreur de communication avec le serveur. Veuillez essayer plus tard.");
        }
    });

    return false;
}

function moveElementToBeginOfParent(element) {
    var parent = element.parent();

    element.detach();

    parent.prepend(element);
};


function update_field_m2m(element_class) {

    $($("#field_wrapper_" + element_class + " ul.select2-selection__rendered").children("li[title]").get().reverse()).each(function(i, obj){
        var element = $("#" + element_class + "_m2m").children("option").filter(function () { return $(this).html() == obj.title; });
        moveElementToBeginOfParent(element);
    });

    fill_input_m2m(element_class);
    $("#field_wrapper_" + element_class).trigger('change');
}

function fill_input_m2m(element_class) {
    text = $("#" + element_class + "_m2m").val().join();
    $("#" + element_class).val(text);
}

