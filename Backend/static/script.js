const API_URL = "http://127.0.0.1:5000";
let token = "";

function scrollToLogin() {
    document.getElementById("login-section").scrollIntoView({ behavior: "smooth" });
}

function registerUser() {
    const username = document.getElementById("user-username").value;
    const password = document.getElementById("user-password").value;

    fetch(`${API_URL}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password, role: "user" }),
    })
    .then(res => res.json())
    .then(data => alert(data.message));
}

function loginUser() {
    const username = document.getElementById("user-username").value;
    const password = document.getElementById("user-password").value;

    fetch(`${API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password, role: "user" }),
    })
    .then(res => res.json())
    .then(data => {
        token = data.token;
        alert("User logged in successfully!");
        loadRestaurants();
    });
}

function registerPartner() {
    const username = document.getElementById("partner-username").value;
    const password = document.getElementById("partner-password").value;

    fetch(`${API_URL}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password, role: "partner" }),
    })
    .then(res => res.json())
    .then(data => alert(data.message));
}

function loginPartner() {
    const username = document.getElementById("partner-username").value;
    const password = document.getElementById("partner-password").value;

    fetch(`${API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password, role: "partner" }),
    })
    .then(res => res.json())
    .then(data => {
        token = data.token;
        alert("Partner logged in successfully!");
    });
}

function loadRestaurants() {
    fetch(`${API_URL}/restaurants`)
    .then(res => res.json())
    .then(data => {
        let html = "<h2>Restaurants</h2>";
        data.forEach(restaurant => {
            html += `<button onclick="loadMenu(${restaurant.id})">${restaurant.name}</button>`;
        });
        document.getElementById("restaurants").innerHTML = html;
    });
}

function loadMenu(restaurantId) {
    fetch(`${API_URL}/menu/${restaurantId}`)
    .then(res => res.json())
    .then(data => {
        let html = "<h2>Menu</h2>";
        data.forEach(item => {
            html += `<p>${item.name} - $${item.price} <button onclick="order(${item.id})">Order</button></p>`;
        });
        document.getElementById("menu").innerHTML = html;
    });
}

function order(menuId) {
    fetch(`${API_URL}/order`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ menu_id: menuId })
    })
    .then(res => res.json())
    .then(data => alert(data.message));
}
