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



function addScore(score,productid){
    var starRatings = document.querySelectorAll(".fa-star")
    starRatings.forEach(element =>{
        element.classList.remove("checked");

    });
    for(let i=1; i<= score; i++){
        const element = document.getElementById("star_" + i);
        element.classList.add("checked")
    }
    $.ajax({
        type:"GET",
        url: "/csf/add_score",
        data:{
            productid: productid,
            score: score,
        },
        success:function(res){
                 // Update the text of the span with the new average score
                document.getElementById("average-score").innerText = res.new_average;
                
                // You can still show a success message if you want
               showToast(res.message, 'success')
                // alert(res.message);
        }
    });
    starRatings.forEach(element =>{
        element.classList.add("disable");
    });



}


function toggleFavorite(productid) {
    $.ajax({
        type: "GET",
        url: "/csf/add_to_favorite/",
        data: {
            productid: productid,
        },
        success: function(res) {
            showToast(res.message, res.type || 'success');

            const favoriteButton = $('#favorite-btn-' + productid);
            const iconElement = favoriteButton.find('i.fa');

            if (res.message.includes('اضافه شد') || res.message.includes('قبلاً اضافه شده است')) {
                // Remove old classes, add new icon and classes for favorited state
                iconElement.removeClass('fa-heart-broken unfavorited-icon').addClass('fa-heart favorited-icon');
            } else if (res.message.includes('حذف شد')) {
                // Remove old classes, add new icon and classes for unfavorited state
                iconElement.removeClass('fa-heart favorited-icon').addClass('fa-heart-broken unfavorited-icon');
            }
        },
        error: function(xhr, status, error) {
            let errorMessage = "خطایی رخ داد. لطفاً دوباره تلاش کنید.";
            let responseJson;
            try {
                responseJson = JSON.parse(xhr.responseText);
                if (responseJson && responseJson.message) {
                    errorMessage = responseJson.message;
                }
            } catch (e) {
س            }

            if (xhr.status === 401 || xhr.status === 403) {
                errorMessage = "برای انجام این عملیات، ابتدا وارد حساب کاربری خود شوید.";
            } else if (xhr.status === 404) {
                errorMessage = "کالا یافت نشد.";
            }

            showToast(errorMessage, 'error');
        }
    });
}


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
                type: "GET", // Or "POST" depending on your Django view setup
                url: "/csf/add_to_favorite/",
                data: {
                    productid: productId,
                },
                success: function(res) {
                    showToast(res.message, res.type || 'success');
                    if (res.message.includes('حذف شد')) {
                        $('#favorite-row-' + productId).remove();
                        // Optional: If the list becomes empty, show a message
                        if ($('.wishlist__body tr').length === 0) {
                            $('.wishlist__body').append(
                                '<tr class="wishlist__row no-favorites">' +
                                    '<td colspan="6" class="text-center py-4">' +
                                        '<p class="text-muted">لیست علاقه مندی های شما خالی است.</p>' +
                                        '<a href="{% url "products:product_list" %}" class="btn btn-primary mt-3">مشاهده محصولات</a>' +
                                    '</td>' +
                                '</tr>'
                            );
                        }
                    }
                },
                error: function(xhr, status, error) {
                    let errorMessage = "خطایی رخ داد. لطفاً دوباره تلاش کنید.";
                    try {
                        let responseJson = JSON.parse(xhr.responseText);
                        if (responseJson && responseJson.message) {
                            errorMessage = responseJson.message;
                        }
                    } catch (e) {
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

// ------------------------------------------------------------------------------------------------------

$(document).ready(function() {
    updateFilterCounts();

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
});





































// function removeURLParametr(url, parametr) {
//     var urlparts = url.split('?');
//     if (urlparts.length >= 2) {
//         var prefix = encodeURIComponent(parametr) + '=';
//         var pars = urlparts[1].split(/[&;]/g);
//         for (var i = pars.length; i-- > 0;) {
//             if (pars[i].lastIndexOf(prefix, 0) !== -1) {
//                 pars.splice(i, 1);
//             }
//         }
//         return urlparts[0] + (pars.length > 0 ? '?' + pars.join('&') : '');
//     }
//     return url;
// }

// function select_sort() {
//     var select_sort_value = $("#select_sort").val();
//     var url = removeURLParametr(window.location.href, "sort_type");
//     if (url.includes('?')) {
//         window.location = url + "&sort_type=" + select_sort_value;
//     } else {
//         window.location = url + "?sort_type=" + select_sort_value;
//     }
// }

// function updateFilterCounts() {
//     // برای هر بخش فیلتر به صورت مجزا اجرا می‌شود
//     $('.widget-filters__item').each(function() {
//         var filterSection = $(this);
//         // تمام عنوان‌های داخل این بخش را پیدا می‌کند (برای بخش ویژگی‌ها مهم است)
//         filterSection.find('.filter__title').each(function() {
//             var titleButton = $(this);
//             // ظرف اصلی هر زیر-بخش را پیدا می‌کند
//             var filterContainer = titleButton.closest('.card, .filter'); 
//             var checkedCount = filterContainer.find('.input-check__input:checked').length;
            
//             titleButton.find('.filter-count').remove();
//             if (checkedCount > 0) {
//                 titleButton.append(' <span class="filter-count">' + checkedCount + '</span>');
//             }
//         });
//     });
// }

// $(document).ready(function() {
//     console.log("Document is ready. Initializing scripts.");

//     // --- راه‌اندازی اولیه ---
//     updateFilterCounts();

//     var urlParams = new URLSearchParams(window.location.search);
//     urlParams.delete('page');
//     if (urlParams.toString() !== "") {
//         $('#reset_filters_btn').css('display', 'inline-block');
//     }
//     // این کد را داخل $(document).ready(...) قرار دهید

//         // رویداد کلیک برای دکمه حذف فیلترها
//         $('#reset_filters_btn').on('click', function() {
//             // با کلیک روی این دکمه، حافظه مربوط به چک‌باکس‌ها را پاک کن
//             localStorage.removeItem('favorites');
//         });

//     var favorites = JSON.parse(localStorage.getItem('favorites'));
//     if (favorites) {
//         favorites.forEach(function(fav) {
//             var element = $('#' + fav.id);
//             if (element.length) {
//                 element.prop('checked', fav.value);
//             }
//         });
//         updateFilterCounts(); 
//     }

//     // --- اسلایدر قیمت ---
//     var priceSliderElement = document.getElementById('price-slider');
//     if (priceSliderElement) {
//         var minPrice = parseInt(priceSliderElement.getAttribute('data-min'));
//         var maxPrice = parseInt(priceSliderElement.getAttribute('data-max'));
//         var startMin = parseInt(urlParams.get('price_min')) || minPrice;
//         var startMax = parseInt(urlParams.get('price_max')) || maxPrice;

//         noUiSlider.create(priceSliderElement, {
//             start: [startMin, startMax],
//             connect: true,
//             step: 100000,
//             range: { 'min': minPrice, 'max': maxPrice },
//             format: {
//                 to: function(value) { return Math.round(value).toLocaleString(); },
//                 from: function(value) { return Number(value.replace(/,/g, '')); }
//             }
//         });

//         var minDisplay = document.getElementById('price-min-display');
//         var maxDisplay = document.getElementById('price-max-display');
//         var minHidden = document.getElementById('price_min_hidden');
//         var maxHidden = document.getElementById('price_max_hidden');

//         priceSliderElement.noUiSlider.on('update', function(values, handle) {
//             var plainValue = Number(values[handle].replace(/,/g, ''));
//             if (handle === 0) {
//                 minDisplay.innerHTML = values[handle];
//                 minHidden.value = plainValue;
//             } else {
//                 maxDisplay.innerHTML = values[handle];
//                 maxHidden.value = plainValue;
//             }
//         });
//     }

//     // --- Event Listeners ---
//     $('#select_sort').on('change', select_sort);

//     $('input:checkbox.input-check__input').on('change', function() {
//         updateFilterCounts();
//         var favs = [];
//         $('input:checkbox.input-check__input').each(function() {
//             favs.push({ id: $(this).attr('id'), value: $(this).prop('checked') });
//         });
//         localStorage.setItem("favorites", JSON.stringify(favs));
//     });
// });











































// // /**
// //  * =================================================================================
// //  * توابع عمومی (Global Functions)
// //  * این توابع باید بیرون از document.ready باشند تا از همه جا قابل دسترس باشند.
// //  * =================================================================================
// //  */

// // // تابع حذف یک پارامتر مشخص از URL
// // function removeURLParametr(url, parametr) {
// //     var urlparts = url.split('?');
// //     if (urlparts.length >= 2) {
// //         var prefix = encodeURIComponent(parametr) + '=';
// //         var pars = urlparts[1].split(/[&;]/g);
// //         for (var i = pars.length; i-- > 0;) {
// //             if (pars[i].lastIndexOf(prefix, 0) !== -1) {
// //                 pars.splice(i, 1);
// //             }
// //         }
// //         return urlparts[0] + (pars.length > 0 ? '?' + pars.join('&') : '');
// //     }
// //     return url;
// // }

// // // تابع اعمال مرتب‌سازی و ریلود صفحه
// // function select_sort() {
// //     console.log("select_sort function called!");
// //     var select_sort_value = $("#select_sort").val();
// //     var url = removeURLParametr(window.location.href, "sort_type");

// //     if (url.includes('?')) {
// //         window.location = url + "&sort_type=" + select_sort_value;
// //     } else {
// //         window.location = url + "?sort_type=" + select_sort_value;
// //     }
// // }

// // // تابع به‌روزرسانی شمارنده فیلترهای انتخاب شده (نسخه اصلاح شده)
// // function updateFilterCounts() {
// //     console.log("Updating filter counts...");

// //     // FIX: به جای widget-filters__item، هر card در آکاردئون را جداگانه بررسی می‌کنیم
// //     $('#accordion .card').each(function() {
// //         var filterSection = $(this);
// //         // عنوان داخل هر card را پیدا می‌کنیم
// //         var titleButton = filterSection.find('.filter__title');
// //         var checkedCount = filterSection.find('.input-check__input:checked').length;

// //         titleButton.find('.filter-count').remove();

// //         if (checkedCount > 0) {
// //             titleButton.append(' <span class="filter-count">' + checkedCount + '</span>');
// //         }
// //     });

// //     // این بخش برای فیلترهایی که ساختار card ندارند (مثل برند) جداگانه اجرا می‌شود
// //     $('.widget-filters__item').not(':has(#accordion)').each(function() {
// //         var filterSection = $(this);
// //         var titleButton = filterSection.find('.filter__title');
// //         var checkedCount = filterSection.find('.input-check__input:checked').length;
        
// //         titleButton.find('.filter-count').remove();

// //         if (checkedCount > 0) {
// //             titleButton.append(' <span class="filter-count">' + checkedCount + '</span>');
// //         }
// //     });
// // }
// // // تابع به‌روزرسانی شمارنده فیلترهای انتخاب شده (نسخه اصلاح شده)
// // // function updateFilterCounts() {
// // //     console.log("Updating filter counts...");

// // //     // FIX: به جای widget-filters__item، هر card در آکاردئون را جداگانه بررسی می‌کنیم
// // //     $('#accordion .card').each(function() {
// // //         var filterSection = $(this);
// // //         // عنوان داخل هر card را پیدا می‌کنیم
// // //         var titleButton = filterSection.find('.filter__title');
// // //         var checkedCount = filterSection.find('.input-check__input:checked').length;

// // //         titleButton.find('.filter-count').remove();

// // //         if (checkedCount > 0) {
// // //             titleButton.append(' <span class="filter-count">' + checkedCount + '</span>');
// // //         }
// // //     });

// //     // این بخش برای فیلترهایی که ساختار card ندارند (مثل برند) جداگانه اجرا می‌شود
// //     $('.widget-filters__item').not(':has(#accordion)').each(function() {
// //         var filterSection = $(this);
// //         var titleButton = filterSection.find('.filter__title');
// //         var checkedCount = filterSection.find('.input-check__input:checked').length;
        
// //         titleButton.find('.filter-count').remove();

// //         if (checkedCount > 0) {
// //             titleButton.append(' <span class="filter-count">' + checkedCount + '</span>');
// //         }
// //     });
// // }
// // // function updateFilterCounts() {
// // //     console.log("Updating filter counts..."); // برای تست در کنسول
// // //     $('.widget-filters__item').each(function() {
// // //         var filterSection = $(this);
// // //         var titleButton = filterSection.find('.filter__title');
// // //         var checkedCount = filterSection.find('.input-check__input:checked').length;

// // //         titleButton.find('.filter-count').remove(); // حذف شمارنده قبلی

// // //         if (checkedCount > 0) {
// // //             titleButton.append(' <span class="filter-count">' + checkedCount + '</span>');
// // //         }
// // //     });
// // // }


// // /**
// //  * =================================================================================
// //  * کدهای اجرایی پس از بارگذاری کامل صفحه (DOM Ready)
// //  * تمام کدهایی که با عناصر صفحه کار می‌کنند باید در اینجا باشند.
// //  * =================================================================================
// //  */

// // $(document).ready(function() {
// //     console.log("Document is ready. Initializing scripts.");


// //     // این کد را داخل $(document).ready(...) قرار دهید

// // // ----------- شروع کد اسلایدر قیمت -----------
// // var priceSlider = document.getElementById('price-slider');

// // if (priceSlider) {
// //     var urlParams = new URLSearchParams(window.location.search);
    
// //     // حداقل و حداکثر قیمت ممکن را از ویو دریافت می‌کنیم
// //     var absMinPrice = {{ res_aggre.min|default:0 }};
// //     var absMaxPrice = {{ res_aggre.max|default:100000000 }};

// //     // مقادیر شروع اسلایدر را از URL یا از مقادیر مطلق می‌خوانیم
// //     var startMinPrice = parseInt(urlParams.get('price_min')) || absMinPrice;
// //     var startMaxPrice = parseInt(urlParams.get('price_max')) || absMaxPrice;

// //     noUiSlider.create(priceSlider, {
// //         start: [startMinPrice, startMaxPrice], // نقاط شروع دستگیره‌ها
// //         connect: true, // رنگی کردن محدوده بین دستگیره‌ها
// //         step: 100000, // گام حرکت دستگیره‌ها
// //         range: {
// //             'min': absMinPrice,
// //             'max': absMaxPrice
// //         },
// //         // برای نمایش اعداد به صورت خوانا (مثلا ۱,۰۰۰,۰۰۰)
// //         format: {
// //           to: function (value) {
// //             return Math.round(value).toLocaleString();
// //           },
// //           from: function (value) {
// //             return Number(value.replace(/,/g, ''));
// //           }
// //         }
// //     });

// //     var minDisplay = document.getElementById('price-min-display');
// //     var maxDisplay = document.getElementById('price-max-display');
// //     var minHiddenInput = document.getElementById('price_min_hidden');
// //     var maxHiddenInput = document.getElementById('price_max_hidden');

// //     // رویدادی که با هر حرکت دستگیره‌ها اجرا می‌شود
// //     priceSlider.noUiSlider.on('update', function (values, handle) {
// //         var plainValue = Number(values[handle].replace(/,/g, '')); // مقدار عددی و بدون کاما
// //         if (handle === 0) { // دستگیره چپ (حداقل)
// //             minDisplay.innerHTML = values[handle];
// //             minHiddenInput.value = plainValue;
// //         } else { // دستگیره راست (حداکثر)
// //             maxDisplay.innerHTML = values[handle];
// //             maxHiddenInput.value = plainValue;
// //         }
// //     });
// // }
// // // ----------- پایان کد اسلایدر قیمت -----------

// //     // ------------------ راه‌اندازی اولیه در زمان بارگذاری صفحه ------------------

// //     // ۱. به‌روزرسانی اولیه شمارنده فیلترها
// //     updateFilterCounts();

// //     // ۲. مدیریت دکمه "حذف فیلترها"
// //     var urlParams = new URLSearchParams(window.location.search);
// //     urlParams.delete('page'); // پارامتر صفحه‌بندی را نادیده بگیر
// //     if (urlParams.toString() !== "") {
// //         $('#reset_filters_btn').css('display', 'inline-block');
// //     }

// //     // ۳. بازیابی وضعیت چک‌باکس‌ها از حافظه مرورگر (localStorage)
// //     var favorites = JSON.parse(localStorage.getItem('favorites'));
// //     if (favorites) {
// //         favorites.forEach(function(fav) {
// //             var element = $('#' + fav.id);
// //             if (element.length) {
// //                 element.prop('checked', fav.value);
// //             }
// //         });
// //         // پس از بازیابی وضعیت، دوباره شمارنده‌ها را به‌روز کن
// //         updateFilterCounts(); 
// //     }

// //     // ------------------ تعریف Event Listener ها ------------------

// //     // ۱. رویداد برای دکمه مرتب‌سازی
// //     $('#select_sort').on('change', select_sort);

// //     // ۲. رویداد برای ذخیره وضعیت چک‌باکس‌ها در حافظه و به‌روزرسانی شمارنده
// //     $('input:checkbox.input-check__input').on('change', function() {
// //         // ابتدا شمارنده را به‌روز کن
// //         updateFilterCounts();

// //         // سپس وضعیت را در حافظه ذخیره کن
// //         var favs = [];
// //         $('input:checkbox.input-check__input').each(function() {
// //             favs.push({ id: $(this).attr('id'), value: $(this).prop('checked') });
// //         });
// //         localStorage.setItem("favorites", JSON.stringify(favs));
// //     });
// // });












// // // // این تابع باید در سطح عمومی باشد تا در دسترس باشد
// // // function removeURLParametr(url, parametr) {
// // //     var urlparts = url.split('?');
// // //     if (urlparts.length >= 2) {
// // //         var prefix = encodeURIComponent(parametr) + '=';
// // //         var pars = urlparts[1].split(/[&;]/g);
// // //         for (var i = pars.length; i-- > 0;) {
// // //             if (pars[i].lastIndexOf(prefix, 0) !== -1) {
// // //                 pars.splice(i, 1);
// // //             }
// // //         }
// // //         return urlparts[0] + (pars.length > 0 ? '?' + pars.join('&') : '');
// // //     }
// // //     return url;
// // // }

// // // // این تابع هم باید در سطح عمومی باشد
// // // function select_sort() {
// // //     // این پیغام برای تست در کنسول نمایش داده می‌شود
// // //     console.log("select_sort function called!"); 

// // //     var select_sort_value = $("#select_sort").val();
// // //     var url = removeURLParametr(window.location.href, "sort_type");

// // //     if (url.includes('?')) {
// // //         window.location = url + "&sort_type=" + select_sort_value;
// // //     } else {
// // //         window.location = url + "?sort_type=" + select_sort_value;
// // //     }
// // // }



// // // // این تابع را بیرون از document.ready تعریف کنید
// // // function updateFilterCounts() {
// // //     // برای هر بخش از فیلتر (مثل برند، ویژگی‌ها و ...)
// // //     $('.filter').each(function() {
// // //         var filterSection = $(this);
// // //         var titleButton = filterSection.find('.filter__title');
// // //         var checkedCount = filterSection.find('.input-check__input:checked').length;

// // //         // ابتدا شمارنده قبلی را حذف می‌کنیم
// // //         titleButton.find('.filter-count').remove();

// // //         // اگر آیتمی انتخاب شده بود، شمارنده جدید را اضافه می‌کنیم
// // //         if (checkedCount > 0) {
// // //             titleButton.append(' <span class="filter-count">' + checkedCount + '</span>');
// // //         }
// // //     });
// // // }


// // // $(document).ready(function() {
// // //     console.log("Document is ready.");

// // // // ////////////////////////////////////////////////////////////    // 

// // // // این دو خط را در داخل $(document).ready(function() { ... }); قرار دهید

// // // // در زمان بارگذاری صفحه، شمارنده‌ها را به‌روز کن
// // // updateFilterCounts();

// // // // با هر بار کلیک روی یک چک‌باکس، دوباره شمارنده‌ها را به‌روز کن
// // // $('.input-check__input').on('change', updateFilterCounts);

// // // // /////////////////////////////////////////////////////////////////

// // //     // این کد را در داخل $(document).ready(function() { ... }); قرار دهید

// // //     var urlParams = new URLSearchParams(window.location.search);

// // //     // پارامتر 'page' را حذف می‌کنیم تا در محاسبات ما به عنوان فیلتر شناخته نشود
// // //     urlParams.delete('page');

// // //     // اگر بعد از حذف 'page'، هنوز پارامتری وجود داشت، یعنی فیلتری فعال است
// // //     if (urlParams.toString() !== "") {
// // //         $('#reset_filters_btn').css('display', 'inline-block');
// // //         }
// // // // /////////////////////////////////////////////////////////////////
// // //     // ۱. اتصال رویداد به مرتب‌سازی (بخش سالم)
// // //     $('#select_sort').on('change', select_sort);

// // //     // ۲. مدیریت دکمه "دارای فیلتر" (بخش سالم)
// // //     var urlParams = new URLSearchParams(window.location.search);
// // //     if (urlParams.toString() === "") {
// // //         localStorage.clear();
// // //         $("#filter_state").css("display", "none");
// // //     } else {
// // //         $("#filter_state").css("display", "inline-block");
// // //     }

// // //     // ۳. مدیریت ذخیره چک‌باکس‌ها (بخش سالم)
// // //     $('input:checkbox').on('click', function() {
// // //         var favs = [];
// // //         $('input:checkbox').each(function() {
// // //             favs.push({ id: $(this).attr('id'), value: $(this).prop('checked') });
// // //         });
// // //         localStorage.setItem("favorites", JSON.stringify(favs));
// // //     });

// // //     // ۴. بازیابی وضعیت چک‌باکس‌ها (نسخه امن و اصلاح شده)
// // //     var favorites = JSON.parse(localStorage.getItem('favorites'));
// // //     if (favorites) {
// // //         favorites.forEach(function(fav) {
// // //             var element = $('#' + fav.id);
// // //             // فقط در صورتی مقدار را تغییر بده که عنصر در صفحه وجود داشته باشد
// // //             if (element.length) {
// // //                 element.prop('checked', fav.value);
// // //             }
// // //         });
// // //     }
// // // });

// // // // این تابع باید در سطح عمومی باشد تا در دسترس باشد
// // // function removeURLParametr(url, parametr) {
// // //     var urlparts = url.split('?');
// // //     if (urlparts.length >= 2) {
// // //         var prefix = encodeURIComponent(parametr) + '=';
// // //         var pars = urlparts[1].split(/[&;]/g);
// // //         for (var i = pars.length; i-- > 0;) {
// // //             if (pars[i].lastIndexOf(prefix, 0) !== -1) {
// // //                 pars.splice(i, 1);
// // //             }
// // //         }
// // //         return urlparts[0] + (pars.length > 0 ? '?' + pars.join('&') : '');
// // //     }
// // //     return url;
// // // }

// // // // این تابع هم باید در سطح عمومی باشد
// // // function select_sort() {
// // //     // این پیغام برای تست در کنسول نمایش داده می‌شود
// // //     console.log("select_sort function called!"); 

// // //     var select_sort_value = $("#select_sort").val();
// // //     var url = removeURLParametr(window.location.href, "sort_type");

// // //     if (url.includes('?')) {
// // //         window.location = url + "&sort_type=" + select_sort_value;
// // //     } else {
// // //         window.location = url + "?sort_type=" + select_sort_value;
// // //     }
// // // }


// // // // کدی که با بارگذاری کامل صفحه اجرا می‌شود
// // // $(document).ready(function() {

// // //     // این پیغام برای تست در کنسول نمایش داده می‌شود
// // //     console.log("Document is ready. Attaching event listener.");

// // //     // اتصال رویداد 'change' به عنصر با آیدی select_sort
// // //     // این جایگزین onchange در HTML است
// // //     $('#select_sort').on('change', function() {
// // //         select_sort();
// // //     });
    
// // //     // بقیه کدهای مربوط به localStorage و فیلترها می‌تواند اینجا باشد
// // //     var urlParams = new URLSearchParams(window.location.search);
// // //     if (urlParams.toString() === "") {
// // //         localStorage.clear();
// // //         $("#filter_state").css("display", "none");
// // //     } else {
// // //         $("#filter_state").css("display", "inline-block");
// // //     }

// // //     // ... بقیه کدهای شما
// // // });







// // // $(document).ready(function() {
// // //     // FIX 1: The correct way to check for empty URL parameters
// // //     var urlParams = new URLSearchParams(window.location.search);
// // //     if (urlParams.toString() === "") {
// // //         localStorage.clear();
// // //         $("#filter_state").css("display", "none");
// // //     } else {
// // //         $("#filter_state").css("display", "inline-block");
// // //     }

// // //     // This logic is fine
// // //     $('input:checkbox').on('click', function() {
// // //         var fav, favs = [];
// // //         $('input:checkbox').each(function() {
// // //             fav = { id: $(this).attr('id'), value: $(this).prop('checked') };
// // //             favs.push(fav);
// // //         });
// // //         localStorage.setItem("favorites", JSON.stringify(favs));
// // //     });

// // //     // FIX 2: Check if 'favorites' exists in localStorage to prevent errors
// // //     var favorites = JSON.parse(localStorage.getItem('favorites'));
// // //     if (favorites) {
// // //         for (var i = 0; i < favorites.length; i++) {
// // //             // Ensure the element exists before trying to modify it
// // //             if ($('#' + favorites[i].id).length) {
// // //                 $('#' + favorites[i].id).prop('checked', favorites[i].value);
// // //             }
// // //         }
// // //     }
// // // });

// // // function showVal(x) {
// // //     // This logic is fine
// // //     x = x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
// // //     // It's better to check if the element exists
// // //     if ($('#sel_price').length) {
// // //         $('#sel_price').text(x);
// // //     }
// // // }

// // // // This function is fine
// // // function removeURLParametr(url, parametr) {
// // //     var urlparts = url.split('?');
// // //     if (urlparts.length >= 2) {
// // //         var prefix = encodeURIComponent(parametr) + '=';
// // //         var pars = urlparts[1].split(/[&;]/g);
// // //         for (var i = pars.length; i-- > 0;) {
// // //             if (pars[i].lastIndexOf(prefix, 0) !== -1) {
// // //                 pars.splice(i, 1);
// // //             }
// // //         }
// // //         return urlparts[0] + (pars.length > 0 ? '?' + pars.join('&') : '');
// // //     }
// // //     return url;
// // // }

// // // // تابع انتخاب مدل مرتب سازی
// // // function select_sort() {
// // //     var select_sort_value = $("#select_sort").val();
// // //     var url = removeURLParametr(window.location.href, "sort_type");

// // //     // FIX 3: Correctly append the sort parameter using '?' or '&'
// // //     if (url.includes('?')) {
// // //         window.location = url + "&sort_type=" + select_sort_value;
// // //     } else {
// // //         window.location = url + "?sort_type=" + select_sort_value;
// // //     }
// // // }

// // // function add_to_shop_cart(product_id, qty) {
// // //     // FIX 4: The first alert was likely for debugging and was syntactically incorrect. Removed it.
// // //     $.ajax({
// // //         type: "GET",
// // //         url: "/orders/add_to_shop_cart/",
// // //         data: {
// // //             product_id: product_id,
// // //             qty: qty,
// // //         },
// // //         success: function(res) {
// // //             alert("کالای مورد نظر به سبد خرید شما اضافه شد");
// // //             $("#indicator__value").text(res);
// // //         }
// // //     });
// // // }

// // // function delete_from_shop_cart(product_id) {
// // //     $.ajax({
// // //         type: "GET",
// // //         url: "/orders/delete_from_shop_cart/",
// // //         data: {
// // //             product_id: product_id,
// // //         },
// // //         success: function(res) {
// // //             alert("کالای مورد نظر از سبد خرید شما حذف شد");
// // //             $("#shop_cart_list").html(res);
// // //         }
// // //     });
// // // }













// // // $(document).ready(
// // //     function(){
// // //         var urlParams=new URLSearchParams(window.location.search);
// // //         if(urlParams==""){
// // //             localStorage.clear();
// // //             $("#filter_state").css("display","none");
// // //         }else{
// // //             $("#filter_state").css("display","inline-block");
// // //         }
// // //         $('input:checkbox').on('click',function(){
// // //             var fav,favs=[];
// // //             $('input:checkbox').each(function(){
// // //                 fav={id:$(this).attr('id'),value:$(this).prop('checked')};
// // //                 favs.push(fav);
// // //             })
// // //             localStorage.setItem("favorites",JSON.stringify(favs));
// // //         })
// // //         var favorites=JSON.parse(localStorage.getItem('favorites'));
       
// // //         for(var i = 0; i < favorites.length; i++){
// // //             $('#' + favorites[i].id).prop('checked', favorites[i].value);
// // //         }
// // //     }
// // // );




// // // function showVal(x) {
// // //     x=x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
// // //     document.getElementById('sel_price').innerText=x;
// // // }



// // // // تابع حذف پارامتر های خط آدرس
// // // function removeURLParametr(url,parametr){
// // //     var urlparts = url.split('?');
// // //     if (urlparts.length >= 2){
// // //         var prefix = encodeURIComponent(parametr) + '=';
// // //         var pars = urlparts[1].split(/[&;]/g);
// // //         for (var i = pars.length; i-- > 0;) {
// // //             if (pars[i].lastIndexOf(prefix,0) !== -1){
// // //                 pars.splice(i,1);
// // //             }
// // //         }
// // //         return urlparts[0] + (pars.length > 0 ? '?' + pars.join('&') : '');
// // //     }
// // //     return url;
// // // }




// // // // تابع انتخاب مدل مرتب سازی
// // // function select_sort(){
// // //     var select_sort_value = $("#select_sort").val();
// // //     var url=removeURLParametr(window.location.href,"sort_type");
// // //     window.location  = url + "&sort_type=" + select_sort_value;
// // // }



// // // function add_to_shop_cart(product_id,qty){
// // //     alert(product_id+"",qty);
// // //     $.ajax({
// // //         type:"GET",
// // //         url:"/orders/add_to_shop_cart/",
// // //         data:{
// // //             product_id: product_id,
// // //             qty: qty,
// // //         },
// // //         success:function(res){
// // //             alert("کالای مورد نظر به سبد خرید شما اضافه شد");
// // //             $("#indicator__value").text(res);
// // //         }
// // //     });

// // // }


// // // function delete_from_shop_cart(product_id){
// // //     $.ajax({
// // //         type:"GET",
// // //         url:"/orders/delete_from_shop_cart/",
// // //         data:{
// // //             product_id:product_id,
// // //         },
// // //         success:function(res){
// // //             alert("کالای مورد نظر از سبد خرید شما حذف شد");
// // //             $("#shop_cart_list").html(res);
// // //         }
// // //     });
// // // }