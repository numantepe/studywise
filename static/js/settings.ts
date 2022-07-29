{
//let webURL = "https://studywise.herokuapp.com";
//let webURL = "http://127.0.0.1:5000";

let msg = document.querySelector(".msg") as HTMLElement;
let username = document.querySelector("#username") as HTMLInputElement;
let email = document.querySelector("#email") as HTMLInputElement;
let password = document.querySelector("#password") as HTMLInputElement;

document.querySelector("#form-submit").addEventListener("click", function (e) {
    e.preventDefault();
    msg.textContent = "";
    if(username.value !== "" &&  email.value !== "" && password.value !== ""){
        let xhttp = new XMLHttpRequest();

        xhttp.onreadystatechange = function() {
            if (this.readyState === 4 && this.status === 200){
                console.log("Response Type " + this.responseType);
                console.log("Response Text " + this.responseText);
               
                if(this.responseText === "USER INFO SUCCESSFULLY UPDATED"){
                    msg.textContent = "User info successfully updated!";
                    msg.style.color = "green";

                    localStorage.setItem("username", username.value);

                    setTimeout(function () {msg.textContent = ""}, 2000);
                } 
                else if(this.responseText === "USERNAME NOT UNIQUE"){
                    msg.textContent = "Username is not unique."
                    msg.style.color = "red";
                }
                else {
                    console.log("Something is very wrong.");
                }
            }
        }
        
        const apiURL = `${webURL}/settings/update`;
        xhttp.open("PUT", apiURL, true);
        xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        xhttp.setRequestHeader('Authorization', localStorage.getItem("auth"));
        xhttp.send(`username=${username.value}&email=${email.value}&password=${password.value}`);
    }
    else {
        msg.textContent = "Please fill in all the blank fields.";
        msg.style.color = "red";
    }
});

document.querySelector("#checkbox").addEventListener("click", function (e) {
    if (password.type === "password") {
        password.type = "text";
    } else {
        password.type = "password";
    }
});

document.querySelector("#delete-account").addEventListener("click", function (e) {
    e.preventDefault();
    if (confirm(`Are you sure that you would like to delete your account?\nThis action cannot be undone.\n\nClick "Ok" if yes, otherwise click "Cancel".`) == true) {
        let xReq : XMLHttpRequest = new XMLHttpRequest();

        xReq.onreadystatechange = function () {
            if (this.readyState === 4 && this.status === 200){
                console.log("Response Type " + this.responseType);
                console.log("Response Text " + this.responseText);              
                localStorage.removeItem("username");
                localStorage.removeItem("auth");
                window.location.replace(`${webURL}/login`);
            }
        }
        
        const apiURL = `${webURL}/settings/delete-account`;
        xReq.open("DELETE", apiURL, true);
        xReq.setRequestHeader('Authorization', localStorage.getItem("auth"));
        xReq.send();
    } else {

    }
});

let xReq : XMLHttpRequest = new XMLHttpRequest();

xReq.onreadystatechange = function () {
    if (this.readyState === 4 && this.status === 200){
        let response = this.responseText;
        if(this.responseText === "INVALID AUTH KEY"){
            setTimeout(function () {window.location.replace(`${webURL}/login`)}, 200);
        }
        else{
            let fields = response.split(" ");
            username.value = fields[0];
            email.value = fields[1];
            password.value = fields[2];
        }
    }else {
        console.log(this.responseType);
    }
}

const apiURL = `${webURL}/settings/get-user-info`;
xReq.open("GET", apiURL, true);
xReq.setRequestHeader('Authorization', localStorage.getItem("auth"));
xReq.send();
}