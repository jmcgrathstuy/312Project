function getColors(){
    document.getElementById("colors").style.display = "block";
}

function updateColor1(){
    document.getElementById("color_button").innerHTML = "Green";
    document.getElementById("colors").style.display = "none";
}
function updateColor2(){
    document.getElementById("color_button").innerHTML = "Blue";
    document.getElementById("colors").style.display = "none";
}
function updateColor3(){
    document.getElementById("color_button").innerHTML = "Red";
    document.getElementById("colors").style.display = "none";
}
function updateColor4(){
    document.getElementById("color_button").innerHTML = "Yellow";
    document.getElementById("colors").style.display = "none";
}

function updateColor(){
    var color = document.getElementById("color_button").innerHTML;

    if (color == "Green"){
        document.body.style.backgroundColor = "#8ebf9b";
        document.body.style.color = "#1c3d21";
        document.getElementById("webpage_name").style.color = "#115924";
        document.getElementById("nav_bar").style.backgroundColor = "#6f8f73";
        document.getElementById("nav_bar").style.borderColor = "#115924";
        document.getElementById("setting_menu").style.borderColor = "#115924";
        document.getElementById("setting_menu").style.backgroundColor = "#6f8f73";
    } else if (color == "Blue"){
        document.body.style.backgroundColor = "#8e9fbf";
        document.body.style.color = "#1c293d";
        document.getElementById("webpage_name").style.color = "#112859";
        document.getElementById("nav_bar").style.backgroundColor = "#6f7a8f";
        document.getElementById("nav_bar").style.borderColor = "#112859";
        document.getElementById("setting_menu").style.borderColor = "#112859";
        document.getElementById("setting_menu").style.backgroundColor = "#6f7a8f";
    } else if (color == "Red"){
        document.body.style.backgroundColor = "#bf8e8e";
        document.body.style.color = "#3d1c1c";
        document.getElementById("webpage_name").style.color = "#591111";
        document.getElementById("nav_bar").style.backgroundColor = "#8f6f6f";
        document.getElementById("nav_bar").style.borderColor = "#591111";
        document.getElementById("setting_menu").style.borderColor = "#591111";
        document.getElementById("setting_menu").style.backgroundColor = "#8f6f6f";
    } else{
        document.body.style.backgroundColor = "#bfbc8e";
        document.body.style.color = "#3d3b1c";
        document.getElementById("webpage_name").style.color = "#594e11";
        document.getElementById("nav_bar").style.backgroundColor = "#8f8a6f";
        document.getElementById("nav_bar").style.borderColor = "#594e11";
        document.getElementById("setting_menu").style.borderColor = "#594e11";
        document.getElementById("setting_menu").style.backgroundColor = "#8f8a6f";
    }
    document.getElementById("color_button").innerHTML = "Colors";
    document.getElementById("message").innerHTML = "Your settings have been updated"
}