{
interface Lesson {
    course: string,
    topic: string
}

//let webURL = "https://studywise.herokuapp.com";
//let webURL = "http://127.0.0.1:5000";

// Utilities

function toggle_nothing_div() : void {
    if(document.querySelectorAll(".lesson").length === 0){
        if(window.location.pathname === "/"){
            let lesson_list = document.querySelector(".lesson-list") as HTMLElement;
            lesson_list.innerHTML = `<div class="nothing">Hooray, there is nothing to study!</div>`;
            lesson_list.style.textAlign = "center";
        }
        else if(window.location.pathname === "/view_all_lessons"){
            let lesson_list = document.querySelector(".lesson-list") as HTMLElement;
            lesson_list.innerHTML = `<div class="nothing">You do not have any lessons in the list.</div>`;
            lesson_list.style.textAlign = "center";
        }
    }
    else{
        document.querySelector(".nothing").remove();
        let lesson_list = document.querySelector(".lesson-list") as HTMLElement;
        lesson_list.style.textAlign = "left";
    }
} 

// Database

function send_message_to_db(method : string, course : string, topic : string, option : string) : void {
    let xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200){
            console.log("Response Type " + this.responseType);
            console.log("Response Text " + this.responseText);
            if(this.responseText === "INVALID AUTH KEY"){
                setTimeout(function () {window.location.replace(`${webURL}/login`)}, 200);
            }
        }
    };
    const apiURL = `${webURL}/api/lessons/modify`;
    xhttp.open(method, apiURL, true);
    xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhttp.setRequestHeader('Authorization', localStorage.getItem("auth"));
    xhttp.send(`course=${course}&topic=${topic}&option=${option}`);
}

function delete_all_selected_lessons_from_db(lessons : Object[]) : void {
    let xhttp = new XMLHttpRequest();

    xhttp.onreadystatechange = function() {
        if (this.readyState === 4 && this.status === 200){
            console.log("Response Type " + this.responseType);
            console.log("Response Text " + this.responseText);
        }
    };

    const apiURL = `${webURL}/api/lessons/modify`;
    xhttp.open("DELETE", apiURL, true);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.setRequestHeader('Authorization', localStorage.getItem("auth"));
    let lessonlistText = JSON.stringify(lessons);
    xhttp.send(lessonlistText);
}

// GUI Stuff

function add_new_lesson_to_lesson_list(lesson_list : Element, new_lesson: Lesson) : void {
    if (window.location.pathname === "/"){
        if(!new_lesson.topic.startsWith("http")){
            lesson_list.insertAdjacentHTML("afterbegin", `<li class="lesson">
            <span class="buttons">
                <button type="button" class="btn btn-green finish">Finish</button>
                <button type="button" class="btn btn-yellow delay">Delay</button>
            </span>
            <span class="lesson-text">${new_lesson.course} --- ${new_lesson.topic}</span>
            </li>`);
        }
        else{
            lesson_list.insertAdjacentHTML("afterbegin", `<li class="lesson">
            <span class="buttons">
                <button type="button" class="btn btn-green finish">Finish</button>
                <button type="button" class="btn btn-yellow delay">Delay</button>
            </span>
            <span class="lesson-text">${new_lesson.course} --- <a href="${new_lesson.topic}" target="_blank">${new_lesson.topic}</a></span>
            </li>`);
        }
    }else if (window.location.pathname === "/view_all_lessons"){
    lesson_list.insertAdjacentHTML("afterbegin", `<li class="lesson">
    <span class="buttons">
        <button type="button" class="btn btn-red delete">Delete</button>
    </span>
    <span class="lesson-text">${new_lesson.course} --- ${new_lesson.topic}</span>
    </li>`);       
    }

    // Add deletion functionality to Red "Delete" button
    if (window.location.pathname === "/view_all_lessons"){
        lesson_list.firstElementChild.firstElementChild.addEventListener("click", function(e) {
        e.preventDefault();
        if (e.target instanceof Element){
            let desc = e.target.parentElement.nextElementSibling.textContent; 
            if (confirm(`Are you sure to delete the lesson below? This action cannot be undone.\n${desc}\n\nClick "Ok" if yes, otherwise click "Cancel".`) == true) {
                // SEND MESSAGE TO SERVER
                send_message_to_db("DELETE", desc.split("---")[0].trim(), desc.split("---")[1].trim(), "");
                e.target.parentElement.parentElement.remove();

                toggle_nothing_div();
            } else {

            }
        }
        else{
            alert("Something is very wrong...");
        };
    });
    } else if (window.location.pathname === "/"){
        // Add deletion functionality to Green "Finish" button
        lesson_list.firstElementChild.firstElementChild.firstElementChild.addEventListener("click", function(e) {
            e.preventDefault();
            if (e.target instanceof Element){
                let desc = e.target.parentElement.nextElementSibling.textContent; 
                // SEND MESSAGE TO SERVER
                send_message_to_db("PUT", desc.split("---")[0].trim(), desc.split("---")[1].trim(), "finish");
                e.target.parentElement.parentElement.remove();
                
                toggle_nothing_div();
                }
            else{
                alert("Something is very wrong...");
            };
        });
        // Add deletion functionality to Yellow "Delay" button
        lesson_list.firstElementChild.firstElementChild.firstElementChild.nextElementSibling.addEventListener("click", function(e) {
            e.preventDefault();
            if (e.target instanceof Element){
                let desc = e.target.parentElement.nextElementSibling.textContent; 
                // SEND MESSAGE TO SERVER
                send_message_to_db("PUT", desc.split("---")[0].trim(), desc.split("---")[1].trim(), "delay");
                e.target.parentElement.parentElement.remove();

                toggle_nothing_div();
            }
            else{
                alert("Something is very wrong...");
            };
        });
    }
}

function set_up_lesson_list(lessons : Lesson[]) : void {

    // set up blue "Add New Lesson" button

    document.querySelector("#add-new-lesson").addEventListener("click", function(e) {
        let new_lesson : Lesson = {} as Lesson;
        new_lesson.course = prompt("What is the course code/name?").trim();
        new_lesson.topic = prompt("Write down the topic or what you learned:").trim();

        if(new_lesson.course !== null && new_lesson.course !== "" && new_lesson.topic !== null && new_lesson.topic !== ""){
            let lesson_list = document.querySelector(".lesson-list");

            // SEND MESSAGE TO SERVER
            send_message_to_db("POST", new_lesson.course, new_lesson.topic, ""); 
            
            add_new_lesson_to_lesson_list(lesson_list, new_lesson); 

            toggle_nothing_div();
        } else {

        }
   });

    if(window.location.pathname === "/view_all_lessons"){
    // Filter/Search List

    document.querySelector("#search-filter").addEventListener("keyup", function(e) {
        e.preventDefault();
        if (e.target instanceof HTMLInputElement){
            let course_input = e.target;
            let course_filter = course_input.value.toUpperCase();

            let li_list = document.querySelectorAll(".lesson");

            for(let i = 0; i < li_list.length; i++){
                let li = li_list[i];
                let span = li_list[i].querySelectorAll("span")[1];
                let txtValue = span.textContent;

                if(txtValue.toUpperCase().indexOf(course_filter) > -1){
                    if(li instanceof HTMLElement){
                        li.style.display = "";

                        li.style.backgroundColor = ""; // THIS IS RELATED TO SELECT-ALL BUTTON - WE ARE DESELECTING HERE
                        let btn = document.querySelector("#select-all-deselect-all");
                        btn.classList.remove("btn-yellow");
                        btn.classList.add("btn-green");
                        btn.textContent = "Select All";
    
                    }
                } else {
                    if(li instanceof HTMLElement){
                        li.style.display = "none";
                    }
                }
            }
        } else {
            alert("Something is very wrong...");
        }
    })

    // Select-All and Delete-All

    document.querySelector("#select-all-deselect-all").addEventListener("click", function(e) {
        e.preventDefault();
        let li_list = document.querySelectorAll(".lesson");

        for (let i = 0; i < li_list.length; i++){
            let li = li_list[i];

            if(li instanceof HTMLElement && e.target instanceof Element){
                if(li.style.display === "") {
                    if(li.style.backgroundColor === ""){
                        li.style.backgroundColor = "rgb(219, 240, 249)";
                        e.target.textContent = "Deselect All";
                        e.target.classList.remove("btn-green");
                        e.target.classList.add("btn-yellow");
                    } else {
                        li.style.backgroundColor = "";
                        e.target.textContent = "Select All";
                        e.target.classList.remove("btn-yellow");
                        e.target.classList.add("btn-green");
                    }
                }
            }
        }
    });

    document.querySelector("#delete-all").addEventListener("click", function(e) {
        e.preventDefault();
        if (confirm(`Are you sure to delete all the selected lessons?\nThis action cannot be undone.\n\nClick "Ok" if yes, otherwise click "Cancel".`) == true) {
            let li_list = document.querySelectorAll(".lesson");
        
            let lesson_list_json : Object[] = [];

            for (let i = 0; i < li_list.length; i++){
                let li = li_list[i];

                if(li instanceof HTMLElement){
                    if(li.style.backgroundColor === "rgb(219, 240, 249)") {
                        let desc = li.firstElementChild.nextElementSibling.textContent; 
                        
                        // SEND MESSAGE TO SERVER
                        lesson_list_json.push({"course" : desc.split("---")[0].trim(), "topic": desc.split("---")[1].trim()}); 
                        li.remove();
                    }
                }
            }

            delete_all_selected_lessons_from_db(lesson_list_json);

            let btn = document.querySelector("#select-all-deselect-all");
            btn.classList.remove("btn-yellow");
            btn.classList.add("btn-green");
            btn.textContent = "Select All";

            toggle_nothing_div();
        } else {

        }
    });

    }
    // Add lessons to HTML from lesson_list

    let lesson_list = document.querySelector(".lesson-list");

    for (let i = 0; i < lessons.length; i++)
    {
        let new_lesson = lessons[i];
        add_new_lesson_to_lesson_list(lesson_list, new_lesson);
    }
}

let xReq : XMLHttpRequest = new XMLHttpRequest();

xReq.onreadystatechange = function () {
    if (this.readyState === 4 && this.status === 200){
        let response = this.responseText;
        if(this.responseText === "INVALID AUTH KEY"){
            setTimeout(function () {window.location.replace(`${webURL}/login`)}, 200);
        }
        else{
            document.querySelector("#logged-in-as").innerHTML = `Logged in as <span id="username-welcome">${localStorage.getItem("username")}</span>`
            let convertedResponse = JSON.parse(response);
            let lessons: Lesson[] = convertedResponse;

            set_up_lesson_list(lessons);

            toggle_nothing_div();
       }
    }else {
        console.log(this.responseType);
    }
}

if (window.location.pathname === "/"){
    const apiURL = `${webURL}/api/lessons/today`;
    xReq.open("GET", apiURL, true);
    xReq.setRequestHeader('Authorization', localStorage.getItem("auth"));
    xReq.send();
} else if (window.location.pathname === "/view_all_lessons"){
    const apiURL = `${webURL}/api/lessons/all`;
    xReq.open("GET", apiURL, true);
    xReq.setRequestHeader('Authorization', localStorage.getItem("auth"));
    xReq.send();
}
}