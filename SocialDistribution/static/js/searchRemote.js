document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('search-form');
    const filterValue = document.getElementById('filter');
    var serverNode;

    document.getElementById('filter-form').addEventListener('submit', function(event) {
        event.preventDefault(); 

        serverNode = filterValue.value;
        console.log(serverNode);
    });

    
    if (!searchForm) {
        console.error('Search form not found');
        return;
    }

    searchForm.addEventListener('submit', function(event) {
        event.preventDefault();


        const currentUserInput = searchForm.querySelector('input[name="user1_id"]');
        const searchQueryInput = searchForm.querySelector('input[name="user2_id"]');

        if (!currentUserInput || !searchQueryInput) {
            console.error('Input fields not found');
            return;
        }

        const currentUser = currentUserInput.value;
        const searchQuery = searchQueryInput.value;
        console.log("current: ", currentUser, "searching --> ", searchQuery, "from", serverNode,);

        // 调用搜索函数并传递搜索查询参数
        searchRemoteUsers(serverNode, currentUser, searchQuery);

        
    });
});


function searchRemoteUsers(serverNode, current, query) {
    const url = `/openapi/search/?query=` + encodeURIComponent(query);

    fetch(url)
        .then(response => response.json())
        .then(data => {
            // 处理搜索结果
            console.log(data);
            if (data.url) {
                fetch(`profile/${current}/${query}`)
                    .then(response => {
                        if (!response.ok) {
                            alert("User not found");
                        }
                        window.location.href = `profile/${current}/${query}`;
                    })
            } else {
                alert("User not found");
            }
        })
        .catch(error => {
            console.error('Error searching remote users:', error);
        });
}


