document.querySelector(".copy").addEventListener("click",()=>{
    let field = document.querySelector("#copy");
    field.select();
   document.execCommand('copy');
   
})