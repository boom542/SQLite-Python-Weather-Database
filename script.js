// This code should send requests to the python server, receive the result and update what the user sees to that result

function SendToPython(){ // make a function. this is ran when the submit button is used.
    // Const is used to ensure nothing is changed again. We don't need to change the values after they are inputted so use this
    const city = document.getElementById("city").value; // get the city selection from the selection made on the site
    const date = document.getElementById("date").value; // Get the date (Assuming anything has been entered)
    const average = document.getElementById("average").checked; // Get if the user wants the average. Use .checked as it is a checkbox.
    const data = { // We create one big object here
        city: city, 
        date: date,
        average: average
    };
    fetch("/process", { // We will run the frontend and backend all in one so we send the request to /process
        method: "POST", // Post is used to send data
        headers: { 
            "Content-Type": "application/json" // Send data as JSON
        },
        body: JSON.stringify(data) // Turn data into JSON
    })

    .then(response => response.json()) // Get the response that will be returned

    .then(data => {
        document.getElementById("response").innerText = data.message; // Get the message we gained from the response and show it on the page
    })
    .catch(error => {
        console.error("Error:", error); // Show an error in the console (Not page) if there is an error
    })

    //console.log(data); // Testing purposes
}