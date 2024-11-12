let users = [];
let sites = [];
var myModal = new bootstrap.Modal(document.querySelector('.modal'));
async function fetchData(){ // Fetch users
    try {
        const response= await fetch("/get_user_data");
        users = await response.json();
    } catch(error) {
        console.error(error);
    }
}

async function fetchSites (){ // Fetch sites
    try {
        const response = await fetch("/get_site_data");
        sites = await response.json();
    } catch(error) {
        console.error(error);
    }
}

async function main(){
    await fetchData();
    await fetchSites();
    console.log(sites);
    console.log(users);

    const modal = document.querySelector('.modal')


    document.addEventListener('click', function(event){
        if (event.target.closest('tr').classList.contains('clickable-row')){
            const targetId = event.target.closest('tr').getAttribute('data-target-id');
            const targetRow = document.getElementById(targetId);
            const targetCaret = event.target.closest('tr').querySelector('.caret');
            const caret = document.querySelectorAll('.caret');
            const editableDivs = targetRow.querySelectorAll('.editableDiv');
            const defaultDivs = targetRow.querySelectorAll('.defaultDiv');
            const dropdown = document.querySelectorAll('.siteNameDropdown');
    
            editableDivs.forEach(div => {
                div.style.display = 'none';
            })
    
            defaultDivs.forEach(div => {
                div.style.display = 'flex';
            })
        
            dropdown.forEach(select => {
                select.innerHTML = ''; // Clear options
                
            });
    
            // Handle Caret Logic
            if(targetRow.style.display === 'table-row'){
                targetRow.style.display = 'none';
            } else {
                document.querySelectorAll('.collapsible-row').forEach(row => {
                    row.style.display = 'none';
                });
                targetRow.style.display = 'table-row';
            }
    
            if (targetCaret.className === 'bi bi-caret-up-fill caret'){
                targetCaret.className = 'bi bi-caret-down-fill caret';
            } else {
                caret.forEach(btn => {
                    btn.className = 'bi bi-caret-down-fill caret';
                });
                targetCaret.className = 'bi bi-caret-up-fill caret';
            }
    
        }
    
        if (event.target.closest('tr').classList.contains('collapsible-row')){
            const sitesCell = event.target.closest('tr').previousElementSibling.querySelector('.colFive');
            const btn = event.target.closest('button');
            const targetId = event.target.closest('tr').id;
            const targetRow = document.getElementById(targetId)
            const editableDivs = targetRow.querySelectorAll(".editableDiv");
            const defaultDivs = targetRow.querySelectorAll(".defaultDiv");
            
            if (btn.classList.contains('edit')){
                
                const defaultSite = btn.closest(".site-div").querySelector(".siteName");
                const siteDropdown = btn.closest(".site-div").querySelector(".siteNameDropdown");
                const editDiv = btn.closest(".site-div").querySelector(".editableDiv");
                const defaultDiv = btn.closest(".site-div").querySelector(".defaultDiv");
                const addDropdown = btn.closest('.td-container').querySelector('.addDropdown');
                editableDivs.forEach(div => {
                    div.style.display = 'none';
                })
        
                defaultDivs.forEach(div => {
                    div.style.display = 'flex';
                })
        
                editDiv.style.display = 'flex';
                defaultDiv.style.display = 'none'; 
                siteDropdown.innerHTML = ''; // Clear sites
                addDropdown.innerHTML = '';
        
                sites.forEach(site => { // Append site options
                    var option = document.createElement('option');
                    option.textContent = site.title;
                    option.id = site.groupId
                    if (defaultSite.innerText === site.title) {
                        option.selected = true;
                        option.disabled = true;      
                    }
                    siteDropdown.appendChild(option);           
                })
            }
        
            if (btn.classList.contains('delete')){
                /*
                const siteDiv = btn.closest('.site-div');
                const siteName = siteDiv.querySelector('.siteName');
                const addDropdown = btn.closest('.td-container').querySelector('.addDropdown');
                const siteDropdown = btn.closest(".site-div").querySelector(".siteNameDropdown");
                */
                myModal.show(btn);


                
            }
        
            if (btn.classList.contains('save')){
                if (btn.closest('.site-container').classList.contains('add-container')){
                    const addDiv = btn.closest('.editableDiv');
                    const addDropdown = addDiv.querySelector('.addDropdown');
                    const selectedAddSite = addDropdown.selectedOptions[0];
        
                    if (!users[(targetId - 1)].sites.includes(selectedAddSite.textContent)){
                        const body = {
                            id: users[(targetId - 1)].id, 
                            new_group_id: parseInt(selectedAddSite.id)
                        }
        
                        fetch("/sites", {
                            method: "POST", 
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify(body)
                        })
                        .then(response => {
                            if (response.ok){
                                const data = response.json();
                                return data
                            } else {
                                throw new Error('Failed to add site: ' + response.status);
                            }
                        })
                        .then(async data =>  {
                            
                            sitesCell.innerText = data.sites.join(" | ");
        
                            await fetchData();
                            await fetchSites();
        
                            const newSiteDiv = document.getElementById(users.find(user => user.id != users[(targetId - 1)].id && user.sites.length > 0).safe_id).querySelector(".site-div").cloneNode(true);
                            newSiteDiv.querySelectorAll('.label').forEach(label => {
                                label.innerText = 'Site: ';
                            })
                            
                            newSiteDiv.querySelector('.siteName').innerText = selectedAddSite.textContent;
                            targetRow.querySelector('.site-container').appendChild(newSiteDiv);
        
                            editableDivs.forEach(div => {
                                div.style.display = 'none';
                            })
                            defaultDivs.forEach(div => {
                                div.style.display = 'flex';
                            })
                
                            addDiv.style.display = 'none';
                            addDropdown.innerHTML = '';
        
                        })
                        .catch(error => {
                            console.error(error)
                        })
                    } else {
                        editableDivs.forEach(div => {
                            div.style.display = 'none';
                        })
                        defaultDivs.forEach(div => {
                            div.style.display = 'flex';
                        })
            
                        addDiv.style.display = 'none';
                    }
                } else {
                    const defaultSite = btn.closest(".site-div").querySelector(".siteName");
                    const siteDropdown = btn.closest(".site-div").querySelector(".siteNameDropdown");
                    const editDiv = btn.closest(".site-div").querySelector(".editableDiv");
                    const defaultDiv = btn.closest(".site-div").querySelector(".defaultDiv");
        
                    const selectedSite = siteDropdown.selectedOptions[0];
        
                    if (users[(targetId - 1)].sites.includes(selectedSite.innerText)) {
                        siteDropdown.innerHTML = '';
                        defaultDiv.style.display = 'flex';
                        editDiv.style.display = 'none';
                        return
                    }
        
                    if (!(users.find(user => user.safe_id === parseInt(targetId)))){
                        console.error("Invalid User!")
                    } else if (!(sites.find(site => site.groupId === parseInt(selectedSite.id)))) {
                        console.error("Invalid Site!")
                    } else {
                        var body = {
                            id: users[(targetId - 1)].id,
                            old_group_id: parseInt(sites.find(site => site.title === defaultSite.innerText).groupId),
                            new_group_id: parseInt(selectedSite.id)
                        }
        
                        fetch("/sites", {
                            method: "PUT", 
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify(body)
                        })
                        .then(response => {
                            if (response.ok) {
                                const data = response.json() 
                                return data;   
                            } else {
                                throw new Error('Failed to update site: ' + response.status);
                            }
                        })
                        .then(async data => {
                            
                            sitesCell.innerText = data.sites.join(" | ")
                            defaultSite.innerText = selectedSite.textContent;
                            siteDropdown.innerHTML = '';
                            defaultDiv.style.display = 'flex';
                            editDiv.style.display = 'none';
                            await fetchSites();
                            await fetchData();
                            console.log(users);
                        })
                        .catch(error => {
                            console.error(error);
                        })
                    }     
        
        
                }
            }
        
            if (btn.classList.contains('cancel')){
                if (btn.closest('.site-container').classList.contains('add-container')){
                    const addDiv = btn.closest('.editableDiv');
                    const addDropdown = addDiv.querySelector('.addDropdown');
                    editableDivs.forEach(div => {
                        div.style.display = 'none';
                    })
                    defaultDivs.forEach(div => {
                        div.style.display = 'flex';
                    })
                    addDropdown.innerHTML = '';
                    addDiv.style.display = 'none';
        
                } else {
                    const editDiv = btn.closest(".site-div").querySelector(".editableDiv");
                    const defaultDiv = btn.closest(".site-div").querySelector(".defaultDiv");
                    const siteDropdown = btn.closest(".site-div").querySelector(".siteNameDropdown");
                    defaultDiv.style.display = 'flex';
                    editDiv.style.display = 'none';
                    siteDropdown.innerHTML = '';
                }
            }
        
            if (btn.classList.contains('add')){
                const addDiv = targetRow.querySelector('.add-container').querySelector('.editableDiv')
                const addDropdown = addDiv.querySelector('.addDropdown');
                editableDivs.forEach(div => {
                    div.style.display = 'none';
                })
                defaultDivs.forEach(div => {
                    div.style.display = 'flex';
                })
                addDiv.style.display = 'inline-flex'
        
                sites.forEach(site => { // Append site options
                    var option = document.createElement('option');
                    option.textContent = site.title;
                    option.id = site.groupId
                    if (!users[(targetId - 1)].sites.includes(option.textContent)) {
                        addDropdown.appendChild(option);      
                    }             
                })
            }
        }
    })

    modal.addEventListener('show.bs.modal', function(event){
        console.log(event.relatedTarget);
        const btn = event.relatedTarget.closest('button');
        const siteDiv = btn.closest('.site-div');
        const siteName = siteDiv.querySelector('.siteName');
        const addDropdown = btn.closest('.td-container').querySelector('.addDropdown');
        const siteDropdown = siteDiv.querySelector(".siteNameDropdown");
        const sitesCell = btn.closest('tr').previousElementSibling.querySelector('.colFive');
        const targetId = btn.closest('tr').previousElementSibling.getAttribute('data-target-id');
        const targetRow = document.getElementById(targetId)
        const editableDivs = targetRow.querySelectorAll(".editableDiv");
        const defaultDivs = targetRow.querySelectorAll(".defaultDiv");
        const confirmButton = modal.querySelector('.confirm');
        const modalCancelButton = modal.querySelector('.modalCancel');

        confirmButton.addEventListener('click', function(){
            editableDivs.forEach(div => {
                div.style.display = 'none';
            })
            defaultDivs.forEach(div => {
                div.style.display = 'flex';
            })
            addDropdown.innerHTML = '';
            siteDropdown.innerHTML = '';
    
            if (users[(targetId - 1)].sites.includes(siteName.innerText)){
    
                const body = {
                    id: users[(targetId - 1)].id,
                    old_group_id: parseInt(sites.find(site => site.title === siteName.innerText).groupId)
                }
    
                fetch("/sites", {
                    method: "DELETE", 
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(body)
                })
                .then(response => {
                    if (response.ok){
                        const data = response.json()
                        return data
                    }
                })
                .then(async data => {
                    sitesCell.innerText = data.sites.join(" | ");
                    await fetchData();
                    await fetchSites();
                    siteDiv.remove();
                    editableDivs.forEach(div => {
                        div.style.display = 'none';
                    })
                    defaultDivs.forEach(div => {
                        div.style.display = 'flex';
                    })
                    addDropdown.innerHTML = '';
                    siteDropdown.innerHTML = '';
                    myModal.hide();
                })
                
            }
            myModal.hide();
        })

        modalCancelButton.addEventListener('click', function(){
            myModal.hide();
        })

        
    })
}
main();


