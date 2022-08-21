{
//let webURL = "https://studywise.herokuapp.com";
//let webURL = "http://127.0.0.1:5000";

let msg = document.querySelector(".msg");
let username = document.querySelector("#username") as HTMLInputElement;
let email = document.querySelector("#email") as HTMLInputElement;
let password = document.querySelector("#password") as HTMLInputElement;
let confirmPassword = document.querySelector("#confirm-password") as HTMLInputElement;

document.querySelector("#form-submit").addEventListener("click", function (e) {
    e.preventDefault();
    msg.textContent = "";
    if(username.value !== "" && email.value !== "" && 
        password.value !== "" && confirmPassword.value !== ""){
        if(password.value === confirmPassword.value){
            let xhttp = new XMLHttpRequest();

            xhttp.onreadystatechange = function() {
                if (this.readyState === 4 && this.status === 200){
                    console.log("Response Type " + this.responseType);
                    console.log("Response Text " + this.responseText);
                    if(this.responseText === "USERNAME NOT UNIQUE"){
                      msg.textContent = "The username is already taken.";
                    }
                    else{
                      localStorage.setItem("username", username.value);
                      localStorage.setItem("auth", this.responseText);
                      window.location.replace(`${webURL}/`);
                    }
                }
            };
            const apiURL = `${webURL}/register/new-user`;
            xhttp.open("POST", apiURL, true);
            xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
            xhttp.send(`username=${username.value}&email=${email.value}&password=${password.value}`);
        }
        else {
            msg.textContent = "The passwords do not match.";
        }
    }
    else {
        msg.textContent = "Please fill in all the blank fields.";
    }
});

document.querySelector("#checkbox").addEventListener("click", function (e) {
    if (password.type === "password") {
      password.type = "text";
    } else {
      password.type = "password";
    }
    if (confirmPassword.type === "password") {
      confirmPassword.type = "text";
    } else {
      confirmPassword.type = "password";
    }
});
}