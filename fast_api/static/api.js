const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");
const messageBox = document.getElementById("message");



const suggestionButtons = document.querySelectorAll(".suggestion button");



suggestionButtons.forEach((button) => {
    button.addEventListener("click", () => {
        userInput.value = button.textContent;
    });
});



async function sendMessage() {

    const text = userInput.value.trim();

    if (text === "") return;


    // USER MESSAGE
    const userMsg = document.createElement("div");
    userMsg.classList.add("user-msg");
    userMsg.textContent = text;

    messageBox.appendChild(userMsg);

    userInput.value = "";


    // BOT LOADING MESSAGE
    const botMsg = document.createElement("div");
    botMsg.classList.add("bot-msg");
    botMsg.textContent = "Thinking...";

    messageBox.appendChild(botMsg);


    try {

        const response = await fetch("http://127.0.0.1:8000/ask", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                question: text
            })

        });

        const data = await response.json();

        // replace loading text
        botMsg.textContent = data.answer;

    } catch (error) {

        botMsg.textContent = "Error connecting to server.";

        console.error(error);
    }


    // auto scroll
    messageBox.scrollTop = messageBox.scrollHeight;
}


// send button
sendBtn.addEventListener("click", sendMessage);


// enter key
userInput.addEventListener("keydown", (e) => {

    if (e.key === "Enter") {
        sendMessage();
    }

});