// all pages consists of title and content
const params = new URLSearchParams(window.location.search);
const name = params.get("name");
const token = params.get("token");

import { adhs_quests } from "./adhs_catalog.js";
import { free_quests } from "./free_catalog.js";
import { gen_quests } from "./gen_catalog.js";


// for each GET page
async function loadGETPage() {
	// fetch title and content from API
	const response = await fetch("/api/get/" + name);
	const data = await response.json();
	document.querySelector("#title").textContent = data.title;
	if (data.content) document.querySelector("#content").innerHTML = data.content;
	document.querySelector("#header").innerHTML = data.title;
	document.querySelector("#info").innerHTML = data.info;


	// einladen
	const invite = document.querySelector("#invite");
	if (invite) {
		invite.addEventListener("submit", async (event) => {
			event.preventDefault();
			const body = Object.fromEntries(new FormData(event.target));
			const response = await fetch("/api/post/einladen", {
				// check safety later. tranfers admin key from client to server
				method: "POST",
				body: new URLSearchParams(body),
			});
			const data = await response.json();
			// redirect
			if (data.ok) { window.location.href = "/eingeladen"; }	
		});
	}

	// einloggen
	const login = document.querySelector("#login");
	if (login && token) { 
		login.addEventListener("submit", async (event) => {
			event.preventDefault();
			const form = new FormData(event.target);
			form.append("token",token)
			const body = Object.fromEntries(form);
			// this response carries the session token!
			const response = await fetch("/api/post/einloggen", {
				method: "POST",
				body: new URLSearchParams(body)
			});
			// would like to check cookie here but appearantly invisible to JS 
			const data = await response.json();
			// redirect
			if (data.ok) { window.location.href = "/einreichen"; }	
		});
	}

	// einreichen
	const test1 = document.querySelector("#test1");
	if (test1) {

		// render form
		const mc3 =  ["Nein", "Vielleicht", "Ja"];
		const mc5 = ["Nie", "Selten", "Manchmal", "Oft", "Sehr oft"];


		document.getElementById("gen_questions").innerHTML = `
			 ${gen_quests.map(i => `
			 		<div class="question">
					<legend> ${i.text} </legend>
					<div class= "answerfield">
					${mc3.map(c => ` 
						<label> 
						<input type="radio" name="${i.id}" value="${c}" required> ${c}
						</label>`).join("")}
					</div>
					</div>`).join("")}
			`;
	

		document.getElementById("adhs_questions").innerHTML = `
			 ${adhs_quests.map(i => `
			 		<div class="question">
					<legend> ${i.text} </legend>
					<div class= "answerfield">
					${mc5.map(c => ` 
						<label> 
						<input type="radio" name="${i.id}" value="${c}" required> ${c}
						</label>`).join("")}
					</div>
					</div>`).join("")}
			`;


		document.getElementById("free_questions").innerHTML = `
			 ${free_quests.map(i => `
			 		<div class="question">
					<legend> ${i.text} </legend>
					<div class= "answerfield">
					<input type="text" name="${i.id}">
					</div>
					</div>`).join("")}
			`;



		test1.addEventListener("submit", async (event) => {
			event.preventDefault();
			const body = Object.fromEntries(new FormData(event.target));
			const response = await fetch("/api/post/einreichen", {
				method: "POST",
				body: new URLSearchParams(body),
				credentials: "include"
			});
			const data = await response.json();
			// redirect
			if (data.ok) { window.location.href = "/eingereicht"; }	
		});
	}
}

if (name) loadGETPage();

