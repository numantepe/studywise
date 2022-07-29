{
//let webURL = "https://studywise.herokuapp.com";
//let webURL = "http://127.0.0.1:5000";

let msg = document.querySelector(".msg");
let username = document.querySelector("#username") as HTMLInputElement;
let password = document.querySelector("#password") as HTMLInputElement;

document.querySelector("#form-submit").addEventListener("click", function (e) {
    e.preventDefault();
    msg.textContent = "";
    if(username.value !== "" &&  password.value !== ""){
        let xhttp = new XMLHttpRequest();

        xhttp.onreadystatechange = function() {
            if (this.readyState === 4 && this.status === 200){
                console.log("Response Type " + this.responseType);
                console.log("Response Text " + this.responseText);
                
                if(this.responseText === "NO SUCH ACCOUNT"){
                    msg.textContent = "No such account with the username provided.";
                }
                else if(this.responseText === "INCORRECT PASSWORD"){
                    msg.textContent = "Incorrect password."; 
                }
                else{
                    localStorage.setItem("username", username.value);
                    localStorage.setItem("auth", this.responseText);
                    window.location.replace(`${webURL}/`);
                }
           }
        }
        
        const apiURL = `${webURL}/login/existing-user`;
        xhttp.open("PUT", apiURL, true);
        xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        xhttp.send(`username=${username.value}&password=${password.value}`);
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
});
}