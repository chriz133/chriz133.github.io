console.log('Happy developing ✨')

const btn = document.getElementsByClassName("btn")[0];

let state = 0;

btn.addEventListener("touchstart", e => {
    btn.style.backgroundColor = "#838383"
})

btn.addEventListener("touchend", e => {
    btn.style.backgroundColor = "#7c4c4c"

})
