function removeURLParametr(url, parametr) {
    var urlparts = url.split('?');
    if (urlparts.length >= 2) {
        var prefix = encodeURIComponent(parametr) + '=';
        var pars = urlparts[1].split(/[&;]/g);
        for (var i = pars.length; i-- > 0;) {
            if (pars[i].lastIndexOf(prefix, 0) !== -1) {
                pars.splice(i, 1);
            }
        }
        return urlparts[0] + (pars.length > 0 ? '?' + pars.join('&') : '');
    }
    return url;
}

function select_sort() {
    var select_sort_value = $("#select_sort").val();
    var url = removeURLParametr(window.location.href, "sort_type");
    if (url.includes('?')) {
        window.location = url + "&sort_type=" + select_sort_value;
    } else {
        window.location = url + "?sort_type=" + select_sort_value;
    }
}

function updateFilterCounts() {
    $('.widget-filters__item').each(function() {
        var filterSection = $(this);
        filterSection.find('.filter__title').each(function() {
            var titleButton = $(this);
            var filterContainer = titleButton.closest('.card, .filter');
            var checkedCount = filterContainer.find('.input-check__input:checked').length;

            titleButton.find('.filter-count').remove();
            if (checkedCount > 0) {
                titleButton.append(' <span class="filter-count">' + checkedCount + '</span>');
            }
        });
    });
}
status_of_shop_cart();


// Min icon Shopcart Counts
function status_of_shop_cart(){
     $.ajax({
        type:"GET",
        url:"/orders/status_of_shop_cart/",     
        success:function(res){
            $("#indicator__value").html(res);
        }
    });
}



// orders_app Scripts
function add_to_shop_cart(product_id,qty){
    if (qty===0){
        qty=$("#product-quantity").val();
    }
    // alert(product_id+"",qty);
    $.ajax({
        type:"GET",
        url:"/orders/add_to_shop_cart/",
        data:{
            product_id: product_id,
            qty: qty,
        },
        // success:function(res){
        //     alert("کالای مورد نظر به سبد خرید شما اضافه شد");
        //     $("#indicator__value").text(res);
        // }
        success: function(response) {
            // $("#indicator__value").text(response);
            status_of_shop_cart();
            // alert("کالای مورد نظر به سبد خرید شما اضافه شد");
            showToast("کالای مورد نظر به سبد خرید شما اضافه شد");

        },
        error: function(xhr, status, error) {
            // This function runs if the request fails
            console.error("AJAX Error:", status, error);
            alert("خطایی در افزودن به سبد خرید رخ داد. لطفاً کنسول را بررسی کنید.");
        }
    });

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
const csrftoken = getCookie('csrftoken');

function delete_from_shop_cart(product_id) {
    $.ajax({
        type: "POST", // <-- تغییر به POST
        url: "/orders/delete_from_shop_cart/",
        data: {
            product_id: product_id,
            csrfmiddlewaretoken: csrftoken // <-- افزودن توکن
        },
        success: function(res) {
            // alert("کالای مورد نظر از سبد خرید شما حذف شد");
            showToast("کالای مورد نظر از سبد خرید شما حذف شد");
            // کل محتوای سبد خرید را با پاسخ جدید جایگزین می‌کنیم
            $("#shop_cart_list").html(res);
            status_of_shop_cart(); // برای آپدیت عدد بالای صفحه
        }
    });
}

function update_shop_cart(event) {
    event.preventDefault(); // جلوگیری از ارسال عادی فرم
    var product_id_list = [];
    var qty_list = [];
    $("input[id^='qty_']").each(function(index) {
        product_id_list.push($(this).attr('id').slice(4));
        qty_list.push($(this).val());
    });

    $.ajax({
        type: "POST", // <-- تغییر به POST
        url: "/orders/update_shop_cart/",
        data: {
            product_id_list: product_id_list,
            qty_list: qty_list,
            csrfmiddlewaretoken: csrftoken // <-- افزودن توکن
        },
        success: function(res) {
            // alert("سبد خرید شما به روز شد");
            showToast("سبد خرید شما به روز شد");
            // کل محتوای سبد خرید را با پاسخ جدید جایگزین می‌کنیم
            $("#shop_cart_list").html(res);
            status_of_shop_cart(); // برای آپدیت عدد بالای صفحه
        }
    });
}

function showToast(message, type = 'success') {
    const colors = {
        success: 'linear-gradient(to right, #00b09b, #96c93d)',
        error: 'linear-gradient(to right, #ff5f6d, #ffc371)'
    };

    Toastify({
        text: message,
        duration: 4000, 
        close: true,
        gravity: "top", 
        position: "center", 
        // backgroundColor: colors[type],
        style: {
            background: colors[type],
        },
        stopOnFocus: true,
    }).showToast();
}



// function addScore(score,productid){
//     var starRatings = document.querySelectorAll(".fa-star")
//     starRatings.forEach(element =>{
//         element.classList.remove("checked");

//     });
//     for(let i=1; i<= score; i++){
//         const element = document.getElementById("star_" + i);
//         element.classList.add("checked")
//     }
//    $.ajax({
//         type: "GET",
//         url: "/csf/add_score",
//         data: {
//             productid: productid,
//             score: score,
//         },
//         success: function(res) {
//             // آپدیت کردن متن میانگین امتیاز
//             $("#average-score").text(res.new_average);
            
//             // پیدا کردن و آپدیت کردن بخش توضیحات امتیاز
//             // این بخش ممکن است نیاز به تغییر selector داشته باشد
//             let ratingDisplay = $(".product-rating-display");
//             if (ratingDisplay.length) {
//                 let descriptionHtml = `
//                     <small class="text-muted">
//                         (از مجموع ${res.total_votes} رای)
//                     </small>
//                 `;
//                 // حذف پیام قدیمی و جایگزینی با پیام جدید
//                 ratingDisplay.find('small').remove();
//                 ratingDisplay.append(descriptionHtml);
//             }
            
//             showToast(res.message, 'success');

//             // غیرفعال کردن ستاره‌ها پس از ثبت رای
//             var starRatings = document.querySelectorAll(".fa-star.cursor-pointer");
//             starRatings.forEach(element => {
//                 element.onclick = null; // حذف رویداد کلیک
//                 element.classList.remove("cursor-pointer");
//                 element.style.cursor = "default";
//             });
//         },
//         error: function() {
//             showToast('خطا در ثبت امتیاز. لطفاً دوباره تلاش کنید.', 'error');
//         }
//     });
// }
function addScore(score, productid) {
    // Update star UI immediately
    var starRatings = document.querySelectorAll(".fa-star");
    starRatings.forEach(element => {
        element.classList.remove("checked");
    });
    for(let i = 1; i <= score; i++) {
        const element = document.getElementById("star_" + i);
        if (element) {
            element.classList.add("checked");
        }
    }

    $.ajax({
        type: "GET",
        url: "/csf/add_score",
        data: {
            productid: productid,
            score: score,
        },
        success: function(res) {
            console.log("Response from server:", res); // Debugging line
            
            // Ensure the response has the expected data
            if (res && res.new_average !== undefined) {
                // Format the average to 2 decimal places
                const average = parseFloat(res.new_average);
                const formattedAverage = average.toFixed(2);
                
                // Update the average score display
                const averageScoreElement = document.getElementById("average-score");
                if (averageScoreElement) {
                    averageScoreElement.textContent = formattedAverage;
                } else {
                    console.error("Element with ID 'average-score' not found");
                }
                
                // Update rating description if available
                if (res.total_votes !== undefined) {
                    const ratingDescription = `(از مجموع ${res.total_votes} رای)`;
                    $(".product-rating-display small").remove();
                    $(".product-rating-display").append(`<small class="text-muted">${ratingDescription}</small>`);
                }
                
                showToast(res.message || "امتیاز شما با موفقیت ثبت شد", 'success');

                // Disable stars after voting
                document.querySelectorAll(".fa-star.cursor-pointer").forEach(element => {
                    element.onclick = null;
                    element.classList.remove("cursor-pointer");
                    element.style.cursor = "default";
                });
            } else {
                showToast('پاسخ سرور نامعتبر است', 'error');
                console.error("Invalid response format:", res);
            }
        },
        error: function(xhr, status, error) {
            showToast('خطا در ثبت امتیاز. لطفاً دوباره تلاش کنید.', 'error');
            console.error("AJAX Error:", status, error);
            
            // Reset stars on error
            document.querySelectorAll(".fa-star").forEach(element => {
                element.classList.remove("checked");
            });
        }
    });
}

// function toggleFavorite(productid) {
//     $.ajax({
//         type: "GET",
//         url: "/csf/add_to_favorite/",
//         data: {
//             productid: productid,
//         },
//         success: function(res) {
//             showToast(res.message, res.type || 'success');

//             const favoriteButton = $('#favorite-btn-' + productid);
//             const iconElement = favoriteButton.find('i.fa');

//             if (res.message.includes('اضافه شد') || res.message.includes('قبلاً اضافه شده است')) {
//                 // Remove old classes, add new icon and classes for favorited state
//                 iconElement.removeClass('fa-heart-broken unfavorited-icon').addClass('fa-heart favorited-icon');
//             } else if (res.message.includes('حذف شد')) {
//                 // Remove old classes, add new icon and classes for unfavorited state
//                 iconElement.removeClass('fa-heart favorited-icon').addClass('fa-heart-broken unfavorited-icon');
//             }
//         },
//         error: function(xhr, status, error) {
//             let errorMessage = "خطایی رخ داد. لطفاً دوباره تلاش کنید.";
//             let responseJson;
//             try {
//                 responseJson = JSON.parse(xhr.responseText);
//                 if (responseJson && responseJson.message) {
//                     errorMessage = responseJson.message;
//                 }
//             } catch (e) {
// س            }

//             if (xhr.status === 401 || xhr.status === 403) {
//                 errorMessage = "برای انجام این عملیات، ابتدا وارد حساب کاربری خود شوید.";
//             } else if (xhr.status === 404) {
//                 errorMessage = "کالا یافت نشد.";
//             }

//             showToast(errorMessage, 'error');
//         }
//     });
// }


// function removeFavorite(productId) {
//     Swal.fire({
//         title: 'آیا مطمئن هستید؟',
//         text: "این محصول از لیست علاقه‌مندی‌های شما حذف خواهد شد.",
//         icon: 'warning',
//         showCancelButton: true,
//         confirmButtonColor: '#d33',
//         cancelButtonColor: '#3085d6',
//         confirmButtonText: 'بله، حذف کن!',
//         cancelButtonText: 'خیر، منصرف شدم'
//     }).then((result) => {
//         if (result.isConfirmed) {
//             $.ajax({
//                 type: "GET", // Or "POST" depending on your Django view setup
//                 url: "/csf/add_to_favorite/",
//                 data: {
//                     productid: productId,
//                 },
//                 success: function(res) {
//                     showToast(res.message, res.type || 'success');
//                     if (res.message.includes('حذف شد')) {
//                         $('#favorite-row-' + productId).remove();
//                         // Optional: If the list becomes empty, show a message
//                         if ($('.wishlist__body tr').length === 0) {
//                             $('.wishlist__body').append(
//                                 '<tr class="wishlist__row no-favorites">' +
//                                     '<td colspan="6" class="text-center py-4">' +
//                                         '<p class="text-muted">لیست علاقه مندی های شما خالی است.</p>' +
//                                         '<a href="{% url "products:product_list" %}" class="btn btn-primary mt-3">مشاهده محصولات</a>' +
//                                     '</td>' +
//                                 '</tr>'
//                             );
//                         }
//                     }
//                 },
//                 error: function(xhr, status, error) {
//                     let errorMessage = "خطایی رخ داد. لطفاً دوباره تلاش کنید.";
//                     try {
//                         let responseJson = JSON.parse(xhr.responseText);
//                         if (responseJson && responseJson.message) {
//                             errorMessage = responseJson.message;
//                         }
//                     } catch (e) {
//                     }

//                     if (xhr.status === 401 || xhr.status === 403) {
//                         errorMessage = "برای انجام این عملیات، ابتدا وارد حساب کاربری خود شوید.";
//                     } else if (xhr.status === 404) {
//                         errorMessage = "کالا یافت نشد.";
//                     }
//                     showToast(errorMessage, 'error');
//                 }
//             });
//         }
//     });
// }


function removeFavorite(productId) {
    Swal.fire({
        title: 'آیا مطمئن هستید؟',
        text: "این محصول از لیست علاقه‌مندی‌های شما حذف خواهد شد.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'بله، حذف کن!',
        cancelButtonText: 'خیر، منصرف شدم'
    }).then((result) => {
        if (result.isConfirmed) {
            $.ajax({
                type: "POST", // <--- CHANGE THIS TO POST
                url: "/csf/add_to_favorite/", // Use the same endpoint
                data: {
                    productid: productId,
                    csrfmiddlewaretoken: csrftoken // <--- ADD CSRF TOKEN
                },
                success: function(res) {
                    showToast(res.message, res.type || 'success');
                    if (res.message.includes('حذف شد') || !res.is_favorite) { // Check is_favorite flag for reliability
                        $('#favorite-row-' + productId).remove();
                        // Optional: If the list becomes empty, show a message
                        if ($('.wishlist__body tr').length === 0) {
                            $('.wishlist__body').html(`
                                <tr class="wishlist__row no-favorites">
                                    <td colspan="6" class="text-center py-4">
                                        <p class="text-muted">لیست علاقه‌مندی‌های شما خالی است.</p>
                                        <a href="{% url 'products:product_list' %}" class="btn btn-primary mt-3">
                                            مشاهده محصولات
                                        </a>
                                    </td>
                                </tr>
                            `);
                        }
                        // Update favorite count after successful removal
                        if (typeof updateFavoriteCount === 'function') {
                            updateFavoriteCount();
                        }
                    } else if (res.is_favorite) { // This means it was added, but removeFavorite shouldn't add
                        // This case should ideally not happen if logic is purely for removal
                        // but it's good to handle or log if the backend adds unexpectedly
                        console.warn("removeFavorite received 'is_favorite' true, implying item was added, not removed.");
                    }
                },
                error: function(xhr, status, error) {
                    let errorMessage = "خطایی رخ داد. لطفاً دوباره تلاش کنید.";
                    try {
                        let responseJson = xhr.responseJSON || JSON.parse(xhr.responseText);
                        if (responseJson && responseJson.message) {
                            errorMessage = responseJson.message;
                        }
                    } catch (e) {
                        console.error("Error parsing response:", e);
                    }

                    if (xhr.status === 401 || xhr.status === 403) {
                        errorMessage = "برای انجام این عملیات، ابتدا وارد حساب کاربری خود شوید.";
                    } else if (xhr.status === 404) {
                        errorMessage = "کالا یافت نشد.";
                    }
                    showToast(errorMessage, 'error');
                }
            });
        }
    });
}

// Function to display Django messages using showToast
function displayDjangoMessages() {
    if (typeof djangoMessages !== 'undefined' && djangoMessages.length > 0) {
        djangoMessages.forEach(msg => {
            let messageText = msg.message;
            let messageType = msg.tags;

            if (messageType.includes('success')) {
                showToast(messageText, 'success');
            } else if (messageType.includes('error') || messageType.includes('danger')) {
                showToast(messageText, 'error');
            } else if (messageType.includes('warning')) {
                showToast(messageText, 'warning'); // Use 'warning' type if defined
            } else {
                showToast(messageText, 'success'); 
            }
        });
        djangoMessages.length = 0; // Clear messages after displaying
    }
}

// Function to display Django form errors
function displayDjangoFormErrors() {
    if (typeof djangoFormErrors !== 'undefined' && djangoFormErrors.length > 0) {
        djangoFormErrors.forEach(errorText => {
            showToast(errorText, 'error'); 
        });
        
    }
}



document.addEventListener('DOMContentLoaded', () => {
    displayDjangoMessages(); // First, display messages from the messages framework
    displayDjangoFormErrors(); // Then, display form validation errors
});



// Function to check and update the status of the compare list UI
function status_of_compare_list() {
    $.ajax({
        type: "GET",
        url: "/products/status_of_compare_list/",
        success: function(res) {
            // Ensure the icon is always visible
            $("#compare_count_icon").show(); 

            // Update the count displayed
            if (Number(res) === 0) {
                $("#compare_count").text('0'); // Display 0 if no items
            } else {
                $("#compare_count").text(res); // Display the actual count
            }
        },
        error: function() {
            // Optional: Handle error case for the status check, e.g., show 0 or a dash
            $("#compare_count_icon").show();
            $("#compare_count").text('?'); // Or '0' or ''
        }
    });
}


// Function to add a product to the compare list
function addToCompareList(productId, productGroupId) {
    $.ajax({
        type: "GET",
        url: "/products/add_to_compare_list/",
        data: {
            'productId': productId,
            'productGroupId': productGroupId
        },
        success: function(response) {
            // اطمینان حاصل کن که response یک رشته نیست
            var message = response.message || response.text || response || 'عملیات با موفقیت انجام شد.';
            showToast(message, 'success');
            status_of_compare_list();
        },
        error: function() {
            showToast('خطایی در افزودن به لیست مقایسه رخ داد.', 'error');
        }
    });
}


function deleteFromCompareList(productId) {
    $.ajax({
        type: "GET",
        url: "/products/delete_from_compare_list/",
        data: {
            // اینجا هم نام پارامتر را 'productId' بگذارید
            'productId': productId
        },
        success: function(response_html) {
            showToast("کالا از لیست مقایسه حذف شد.", 'success');
            status_of_compare_list();
            // این بخش برای به‌روزرسانی جدول مقایسه بدون رفرش صفحه است
            $("#compare_list").html(response_html);
        },
        error: function() {
            showToast('خطا در حذف از لیست مقایسه.', 'error');
        }
    });
}



function toggleFavorite(productid) {
    // نمایش اسپینر در حین انجام عملیات
    const favoriteButton = $('#favorite-btn-' + productid);
    const iconElement = favoriteButton.find('i.fa');
    iconElement.removeClass('fa-heart fa-heart-broken').addClass('fa-spinner fa-spin');
    
    $.ajax({
        type: "POST", // بهتر است از POST استفاده شود
        url: "/csf/add_to_favorite/",
        data: {
            productid: productid,
            // csrfmiddlewaretoken: '{{ csrf_token }}' // اضافه کردن توکن CSRF
            csrfmiddlewaretoken: csrftoken ,

        },
        success: function(res) {
            showToast(res.message, res.type || 'success');

            // به‌روزرسانی آیکون
            if (res.is_favorite) {
                iconElement.removeClass('fa-spinner fa-spin fa-heart-broken unfavorited-icon')
                           .addClass('fa-heart favorited-icon');
            } else {
                iconElement.removeClass('fa-spinner fa-spin fa-heart favorited-icon')
                           .addClass('fa-heart-broken unfavorited-icon');
            }
            
            // به‌روزرسانی شمارنده علاقه‌مندی‌ها
            if (typeof updateFavoriteCount === 'function') {
                updateFavoriteCount();
            }
            
            // به‌روزرسانی وضعیت در صفحه لیست علاقه‌مندی‌ها (اگر در آن صفحه هستیم)
            if (window.location.pathname.includes('user_favorite') && !res.is_favorite) {
                $('#favorite-row-' + productid).remove();
                
                // اگر لیست خالی شد
                if ($('.wishlist__body tr').length === 0) {
                    $('.wishlist__body').html(`
                        <tr class="wishlist__row no-favorites">
                            <td colspan="6" class="text-center py-4">
                                <p class="text-muted">لیست علاقه‌مندی‌های شما خالی است.</p>
                                <a href="{% url 'products:product_list' %}" class="btn btn-primary mt-3">
                                    مشاهده محصولات
                                </a>
                            </td>
                        </tr>
                    `);
                }
            }
        },
        error: function(xhr, status, error) {
            // بازگرداندن آیکون به حالت قبلی
            const wasFavorite = iconElement.hasClass('fa-heart');
            iconElement.removeClass('fa-spinner fa-spin')
                       .addClass(wasFavorite ? 'fa-heart favorited-icon' : 'fa-heart-broken unfavorited-icon');
            
            // مدیریت خطاها
            let errorMessage = "خطایی رخ داد. لطفاً دوباره تلاش کنید.";
            
            try {
                const responseJson = xhr.responseJSON || JSON.parse(xhr.responseText);
                if (responseJson && responseJson.message) {
                    errorMessage = responseJson.message;
                }
            } catch (e) {
                console.error("Error parsing response:", e);
            }

            if (xhr.status === 401 || xhr.status === 403) {
                errorMessage = "برای انجام این عملیات، ابتدا وارد حساب کاربری خود شوید.";
                // ریدایرکت به صفحه لاگین در صورت نیاز
                window.location.href = '/accounts/login/?next=' + encodeURIComponent(window.location.pathname);
            } else if (xhr.status === 404) {
                errorMessage = "کالا یافت نشد.";
            }

            showToast(errorMessage, 'error');
        }
    });
}

// تابع جدید برای به‌روزرسانی شمارنده علاقه‌مندی‌ها
function updateFavoriteCount() {
    $.ajax({
        type: "GET",
        url: "/csf/status_of_favorite_list/",
        success: function(count) {
            $('#favorite_count').text(count);
        },
        error: function() {
            console.error("خطا در دریافت تعداد علاقه‌مندی‌ها");
        }
    });
}

// ------------------------------------------------------------------------------------------------------

$(document).ready(function() {
    updateFilterCounts();
    updateFavoriteCount();
    status_of_compare_list();
    var urlParams = new URLSearchParams(window.location.search);
    urlParams.delete('page');
    if (urlParams.toString() !== "") {
        $('#reset_filters_btn').css('display', 'inline-block');
    }

    var favorites = JSON.parse(localStorage.getItem('favorites'));
    if (favorites) {
        favorites.forEach(function(fav) {
            var element = $('#' + fav.id);
            if (element.length) {
                element.prop('checked', fav.value);
            }
        });
        updateFilterCounts();
    }

    var priceSliderElement = document.getElementById('price-slider');
    if (priceSliderElement) {
        var minPrice = parseInt(priceSliderElement.getAttribute('data-min'));
        var maxPrice = parseInt(priceSliderElement.getAttribute('data-max'));
        var startMin = parseInt(urlParams.get('price_min')) || minPrice;
        var startMax = parseInt(urlParams.get('price_max')) || maxPrice;

        noUiSlider.create(priceSliderElement, {
            start: [startMin, startMax],
            connect: true,
            step: 100000,
            range: { 'min': minPrice, 'max': maxPrice },
            format: {
                to: function(value) { return Math.round(value).toLocaleString(); },
                from: function(value) { return Number(value.replace(/,/g, '')); }
            }
        });

        var minDisplay = document.getElementById('price-min-display');
        var maxDisplay = document.getElementById('price-max-display');
        var minHidden = document.getElementById('price_min_hidden');
        var maxHidden = document.getElementById('price_max_hidden');

        priceSliderElement.noUiSlider.on('update', function(values, handle) {
            var plainValue = Number(values[handle].replace(/,/g, ''));
            if (handle === 0) {
                minDisplay.innerHTML = values[handle];
                minHidden.value = plainValue;
            } else {
                maxDisplay.innerHTML = values[handle];
                maxHidden.value = plainValue;
            }
        });
    }

    $('#select_sort').on('change', select_sort);
    
    $('#reset_filters_btn').on('click', function() {
        localStorage.removeItem('favorites');
    });

    $('input:checkbox.input-check__input').on('change', function() {
        updateFilterCounts();
        var favs = [];
        $('input:checkbox.input-check__input').each(function() {
            favs.push({ id: $(this).attr('id'), value: $(this).prop('checked') });
        });
        localStorage.setItem("favorites", JSON.stringify(favs));
    });

     const productsScrollContainer = $('.products-carousel-container'); // نام سلکتور را به درستی تنظیم کنید
    const scrollAmount = 300; 

    $('.block-header__arrow--left').on('click', function() {
        productsScrollContainer.animate({
            scrollLeft: productsScrollContainer.scrollLeft() - scrollAmount
        }, 300);
    });

    $('.block-header__arrow--right').on('click', function() {
        productsScrollContainer.animate({
            scrollLeft: productsScrollContainer.scrollLeft() + scrollAmount
        }, 300);
    });
});

