document.querySelector("#logout").addEventListener("click", function (e) {
    e.preventDefault();
    let xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200){
            console.log("Response Type " + this.responseType);
            console.log("Response Text " + this.responseText);
            localStorage.removeItem("auth");
            window.location.replace("http://127.0.0.1:5000/login");
        }
    };

    const apiURL = "http://127.0.0.1:5000/logout";
    xhttp.open("GET", apiURL, true);
    xhttp.setRequestHeader("Authorization", localStorage.getItem("auth"));
    xhttp.send();
});