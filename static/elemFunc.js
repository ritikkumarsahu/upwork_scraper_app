function populateCountries(){
    ungrouped_countries = ['America','China','Russia','Ukrain','Japan']
    grouped_countries = ['Nepal','Bhutan','India']
    let ungrouped = document.getElementById("ungrouped");
    let grouped = document.getElementById("grouped");
    ungrouped.innerHTML = '';
    grouped.innerHTML = '';
    ungrouped_countries.forEach((e)=> {
        let div = document.createElement("div");
        div.classList = ["dropdown-item"];
        div.innerHTML = `<label>${e}</label>
        <input name="chk" type="checkbox" onclick="group(this)" />`
        ungrouped.appendChild(div);
    });
    grouped_countries.forEach((e)=> {
        let div = document.createElement("div");
        div.classList = ["dropdown-item"];
        div.innerHTML = `<label>${e}</label>
        <input name="chk" type="checkbox" onclick="group(this)" checked="checked"/>`
        grouped.appendChild(div);
    });
}
populateCountries();
function countryDropdown() {
    document.getElementById("myDropdown").classList.toggle("show");
}

function filterFunc() {
    let input, filter, a, i;
    input = document.getElementById("myInput");
    filter = input.value.toUpperCase();
    div = document.getElementById("myDropdown");
    a = div.getElementsByTagName("label");
    for (i = 0; i < a.length; i++) {
    txtValue = a[i].textContent || a[i].innerText;
    if (txtValue.toUpperCase().indexOf(filter) > -1) {
        a[i].style.display = "";
    } else {
        a[i].style.display = "none";
    }
    }
}

function selects(){  
    let ele=document.getElementsByName('chk');  
    for(var i=0; i<ele.length; i++){  
        if(ele[i].type=='checkbox')  
            ele[i].checked=true;  
    }  
}  

function deSelect(){  
    let ele=document.getElementsByName('chk');  
    for(var i=0; i<ele.length; i++){  
        if(ele[i].type=='checkbox')  
            ele[i].checked=false;  
        
    }  
}         


function srt(e) {
    // const lis = document.getElementById('')
    const sorted = [...e.children]
        .sort((a, b) => {
        return a.firstElementChild.innerHTML.localeCompare(b.firstElementChild.innerHTML)
        });
    return sorted;

}

function group(e) {
    let group = document.getElementById("grouped");
    let ungroup = document.getElementById("ungrouped");

    if(e.checked == true) {
    group.appendChild(e.parentElement);
    // ungroup.removeChild(e.parentElement);
    }
    else {
    ungroup.appendChild(e.parentElement);
    // group.removeChild(e.parentElement);
    }
    
    const sortedUngroup = srt(ungroup);
    ungroup.innerHTML = "";
    sortedUngroup.forEach((e)=> ungroup.appendChild(e));
    const sortedGroup = srt(group);
    group.innerHTML = "";
    sortedGroup.forEach((e)=> group.appendChild(e));
}

function selectAllCountries(e) {
    let grouped = document.getElementById("grouped");
    let ungrouped = document.getElementById("ungrouped");
    if(e.checked == true) {

    let ungroupedArray = [...ungrouped.children];
    ungroupedArray.forEach((e)=> {e.lastElementChild.checked = true;
                    group(e.lastElementChild);})
    }
    else{
        let groupedArray = [...grouped.children];
        groupedArray.forEach((e)=> {
                        e.lastElementChild.checked = false;
                        group(e.lastElementChild);
                    })	  
    }
}
