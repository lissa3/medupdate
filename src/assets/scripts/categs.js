//click button Categories-> toggle categs
document.addEventListener('click',(e)=>{
  let isCategBut = e.target.matches("[data-dropdown-but]");
    if(!isCategBut&&e.target.closest("[data-dropdown]")!=null){
        return
    }
    if(isCategBut){
      // click button will show<->hide all categories
      const but = document.getElementById("show-cats")
      const ulMenu = document.querySelector(".root-cats");
      if(!but.classList.contains('hide')){
        but.classList.add("hide")
        but.innerHTML="Показать категории"
        ulMenu.classList.remove("to-show")
      }else{
        but.classList.remove('hide')
        but.innerHTML="Спрятать категории"
        ulMenu.classList.add("to-show");
      }
    }
  });
  // help func to outroll (sub)categs;
  //maybe: custom click event(?)
  // by now: mouseover -> outroll categs; click -> make request
let catSideBar = document.querySelector(".root-cats");
if(catSideBar){
  catSideBar.addEventListener("mouseover",(e)=>{
    const isDropDownLink = e.target.matches('[data-dropdown-link]');
    if(!isDropDownLink&&e.target.closest("[data-li]")!=null){
      return
    }
    if(isDropDownLink){
      // get ul children (sibling "a" tag enbed in "li")
      let currentDropDown = e.target.nextElementSibling;
      // e.target is a a tag node-link to-toggle
      currentDropDown.classList.add("to-block");
    }
})
}