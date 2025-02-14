console.log('Happy developing ✨')

const btn = document.getElementsByClassName("btn")[0];
const ico = document.getElementById("ico");
const header = document.getElementById("header");
const submit = document.getElementById("submit");
const input = document.getElementById("code");
const err = document.getElementById("err");
const wrapper = document.getElementById("wrapper");
const divMain = document.getElementById("noZoomDiv");
const audio = document.getElementById("myAudio");


submit.addEventListener("click", function () {
    if (input.value === "2811") {
        wrapper.style.display = "none";
        divMain.style.display = "flex";
        audio.play();
        audio.volume = 0.05;
    }else {
        err.style.display = "block";
    }
})

let state = 0;

const text = ["Du", "Bist", "Einzigartig", "Und", "Wundervoll", "", "...", "<3", "&#9993;",
    `Liebe Samara, <br><br>

heute ist Valentinstag, und auch wenn wir uns leider nicht sehen können, bist du in meinen Gedanken ganz nah. Vielleicht hast du auch aktuell keine Lust auf so einen Tag aber ich möchte dir trotzdem kurz was sagen. Ich hoffe, du weißt, wie viel du mir bedeutest. Jedes "Hab dich lieb" von dir macht meinen Tag ein kleines bisschen schöner, und ich hoffe, dass meine Worte heute dasselbe für dich tun. <br><br>

Es tut mir leid, dass du aktuell viel zum verarbeiten hast. Ich wünschte, ich könnte gerade bei dir sein, dich in den Arm nehmen und dir ein Lächeln ins Gesicht zaubern. Aber ich verspreche dir, sobald es geht und du willst, holen wir das nach! Dann bekommst du nicht nur die schönsten Blumen, sondern auch die Zeit und Aufmerksamkeit, die du verdienst.<br><br>

In der Vergangenheit wurde auf deine Gefühle oft zu wenig Rücksicht genommen, aber das wird sich ändern. In der Zukunft sollen deine Gedanken, Wünsche und Emotionen die höchste Priorität haben. Du verdienst es, gesehen und verstanden zu werden. Ich werde immer für dich da sein, nicht nur an guten Tagen, sondern auch dann, wenn es schwerfällt. Schritt für Schritt, ohne Druck, aber mit ganz viel Herz. <br><br>

Bis dahin denke ich an dich und schicke dir eine große Umarmung. Hab einen schönen Tag, so schön, wie du es bist. <br><br>

Hab dich lieb! ❤️`, "»Ohana heißt Familie. Familie heißt, dass alle zusammenhalten und füreinander da sind.«"]

btn.addEventListener("touchstart", e => {
    btn.style.backgroundColor = "#838383"
})

btn.addEventListener("touchend", e => {
    btn.style.backgroundColor = "#7c4c4c"
    if (state === 5){
        let img = document.createElement("img");
        img.src = "images/silhouette-3078440_960_720.webp"; // Beispielbild
        img.height = 600;
        ico.innerHTML = ""
        ico.appendChild(img);
        state++;
    }
    else if (state === 8){
        ico.classList.remove("text");
        ico.classList.add("ico");
        ico.innerHTML = text[state++];
        btn.innerHTML = "Öffnen"
    }
    else if (state === 9){
        doState0();
        ico.classList.add("text-long");
        header.style.visibility = 'hidden';
        header.style.margin = '10px';
    }
    else if (state === 10){
        doState0();
        header.style.margin = "30%";
        ico.style.textAlign = "center";
        ico.style.fontWeight = "bold";
        ico.style.marginBottom = "300px";
    }
    else if (state === 11){
        let img = document.createElement("img");
        img.src = "images/elegant-pink-floral-bouquet-on-black-background-digital-art_10976322.png"; // Beispielbild
        img.height = 600;
        ico.innerHTML = ""
        ico.appendChild(img);
        header.style.margin = "10%";
        ico.style.marginBottom = "200px";
        let p = document.createElement("p");
        p.innerHTML = "Ich kann dir heut nur digitale Blumen senden!"
        ico.appendChild(p);
        state++;
    }
    else if (state === 12){
        ico.firstChild.src = "images/20140615_181602.jpg"
        ico.firstChild.height  = 900;
        ico.style.marginBottom = "100px";
        ico.children[1].innerHTML = "Falls du solange durchgecklickt hast, hier a bild von mir von vor ca. 11 Jahren (net lachen :D)"
        state++;
    }
    else if (state === 13){
        ico.removeChild(ico.firstChild);
        // ico.removeChild(ico.children[0]);
        ico.children[0].innerHTML = "THE END!"
        ico.children[0].style.fontSize = "5rem"
        ico.style.textAlign = "start"
        let p = document.createElement("p");
        p.style.fontWeight = "lighter";
        p.style.fontSize = "3rem"
        p.innerHTML = `<strong>S</strong>upersüß<br>
                        <strong>A</strong>temberaubend<br>
                        <strong>M</strong>utig<br>
                        <strong>A</strong>ufmerksam<br>
                        <strong>R</strong>ücksichtsvoll<br>
                        <strong>A</strong>nmutig<br>`
        ico.appendChild(p);
        btn.style.visibility = 'hidden';
    }
    else{
        doState0();
    }

})

function doState0() {
    console.log(state);
    ico.classList.remove("ico");
    ico.classList.add("text");
    ico.innerHTML = text[state++];
    btn.innerHTML = "Weiter"
}
