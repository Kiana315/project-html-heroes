
document.addEventListener('DOMContentLoaded', (event) => {
    // Get elements
    var imageDatas = [];

    const textModal = document.getElementById("newTextPost");
    const imageModal = document.getElementById("newImagePost");
    const btn = document.getElementById("floating-button");
    const textForm = document.getElementById("newTextForm");
    const imageForm = document.getElementById("newImageForm");
    const postType = document.getElementById("post-option");
    const textBtn = document.getElementById("text-post");
    const imageBtn = document.getElementById("image-post");

    const imageUploadInput = document.getElementById('imageUpload');
    const previewContainer = document.getElementById('imagePreviewContainer'); 

    // Open pop-up window when clicking floating button
    btn.addEventListener('click', function() {
        postType.style.display = "block";
    });

    textBtn.addEventListener('click', function() {
        textModal.style.display = "block";
        postType.style.display = "none";
    });
    imageBtn.addEventListener('click', function() {
        imageModal.style.display = "block";
        postType.style.display = "none";
    });

    
    window.onclick = function(event) {
        if (event.target === postType) {
            postType.style.display = "none";
        }
        if (event.target === imageModal) {
            imageModal.style.display = "none";
        }
        if (event.target === textModal) {
            textModal.style.display = "none";
        }
    }
    
    textForm.onsubmit = function(event) {
        event.preventDefault(); // Prevent form default submission behavior

        let useCommonMark = document.getElementById('content_type').checked;
        let contentType = useCommonMark ? 'COMMONMARK' : 'PLAIN';

        // Create FormData Obj
        var formData = new FormData(textForm);
        formData.append("content_type", contentType);
        for (var pair of formData.entries()) {
            console.log(pair[0]+ ', ' + pair[1]); 
        }

        if (event.submitter.innerText === "Save Draft"){
            formData.append("is_draft", "true")
        }

        // Send AJAX request to server
        fetch('/api/nps/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken') // Get CSRF token
            },
            credentials: 'same-origin' // For CSRF token verification
        })
        .then(response => {
            if(response.ok) {
                window.location.reload();
                return response.json();
            } else {
                // emptyPost();
                throw new Error('Something went wrong');
            }
        })
        .then(data => {
            // After posted
            textModal.style.display = "none"; // Close pop-up window
            // submitPost();

        })
        .catch((error) => {
            console.error('Error:', error);
            
        });
    };

    // Preview images
    imageUploadInput.addEventListener('change', function(event) {
        if (this.files && this.files[0]) {
            var reader = new FileReader();
 
            reader.onload = function(e) {
                var imageData = e.target.result;    // 获取Base64编码的图像数据
                imageDatas.push(imageData);     // 将图片数据添加到全局数组中
                console.log("images>>>>>> ", imageDatas);
                var imgElement = document.createElement('img');
                imgElement.src = imageData;
                imgElement.style.width = 'auto'; 
                imgElement.style.maxWidth = '150px';
                imgElement.style.height = 'auto';
                imgElement.style.maxHeight = '150px';
                imgElement.style.marginRight = '15px'; 

                previewContainer.appendChild(imgElement); 

                imageForm.onsubmit = function(event) {
                    event.preventDefault(); // Prevent form default submission behavior
                
                    let useCommonMark = document.getElementById('content_type').checked;
                    let contentType = useCommonMark ? 'COMMONMARK' : 'PLAIN';
            
                    // 创建 FormData 对象
                    var formData = new FormData(imageForm);
                    formData.append("content_type", contentType);
            
                    // 将存储在 imageDatas 数组中的图片数据附加到 FormData 对象中
                    
                    
                    formData.append('image_data', imageDatas);
                    
            
                    for (var pair of formData.entries()) {
                        console.log(pair[0]+ ', ' + pair[1]); 
                    }
            
                    // 发送 AJAX 请求到服务器
                    fetch('/api/nps/', {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken') // 获取 CSRF token 的方法
                        },
                        credentials: 'same-origin' // 同源请求，用于 CSRF token 验证
                    })
                    .then(response => {
                        if(response.ok) {
                            window.location.reload();
                            return response.json();
                        } else {
                            // emptyPost();
                            throw new Error('Something went wrong');
                            alert('Some error occurred.');
                        }
                    })
                    .then(data => {
                        // 提交后执行的操作
                        imageModal.style.display = "none"; // 关闭弹出窗口
                        // submitPost();
                        console.log(data);
                    })
                    .catch((error) => {
                        console.error('Error:', error);
                        alert('Some error occurred.');
                    });
                };
            }
            reader.readAsDataURL(this.files[0]); 
        }
    });

});

// Click the x to close the pop-up window
function closeModal() {
    const textModal = document.getElementById("newTextPost");
    const imageModal = document.getElementById("newImagePost");
    imageModal.style.display = "none";
    textModal.style.display = "none";
    console.log("call close")
}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
