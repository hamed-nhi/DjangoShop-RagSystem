// $(document).ready(function(){
//     var listOfElements = $('select[id^="id_product_features-"][id$="-feature"]')
//     $(listOfElements).on('change', function(){
//         f_id = $(this).val();
//         dd1=$(this).attr('id');
//         dd2=dd1.replace("-feature","-filter_value");
//         $.ajax({
//             type:"GET",
//             url:"/products/ajax_admin/?feature_id=" + f_id,
//             success:function(res){
//                 cols = document.getElementById(dd2)
//                 cols.options.length = 0;
//                 for (var k in res) {
//                     cols.options.add(new Option(k,res[k]));
//                 }
//             }
//         });
//     });
// });


// $(document).ready(function() {

//     // تابع اصلی که منطق شما را در خود دارد
//     function updateValues(featureDropdownElement) {
//         var feature_id = $(featureDropdownElement).val();

//         // اگر هیچ ویژگی انتخاب نشده باشد، کاری نکن
//         if (!feature_id) {
//             return;
//         }

//         var id_attribute = $(featureDropdownElement).attr('id');
//         var target_dropdown_id = id_attribute.replace("-feature", "-filter_value");
//         var target_dropdown = $('#' + target_dropdown_id);

//         // مقدار فعلی (ذخیره شده) را می‌خوانیم تا بعداً دوباره انتخابش کنیم
//         var previously_selected_value = target_dropdown.val();

//         $.ajax({
//             type: "GET",
//             url: "/products/ajax_admin/?feature_id=" + feature_id,
//             success: function(res) {
//                 var cols = document.getElementById(target_dropdown_id);
//                 cols.options.length = 0; // خالی کردن گزینه‌های قبلی

//                 // افزودن یک گزینه خالی اولیه
//                 $(cols).append(new Option("---------", ""));

//                 // پر کردن دراپ‌داون با گزینه‌های جدید
//                 for (var k in res) {
//                     $(cols).append(new Option(k, res[k]));
//                 }

//                 // انتخاب مجدد مقداری که از قبل ذخیره شده بود
//                 if (previously_selected_value) {
//                     $(cols).val(previously_selected_value);
//                 }
//             },
//             error: function(xhr, status, error) {
//                 console.error("Failed to fetch values:", status, error);
//             }
//         });
//     }

//     // --- بخش اجرایی ---

//     // 1. برای سطرهای قدیمی: به محض لود شدن صفحه، تابع آپدیت را برای هر سطر اجرا کن
//     $('select[id^="id_product_features-"][id$="-feature"]').each(function() {
//         updateValues(this);
//     });

//     // 2. برای سطرهای جدید یا تغییر سطرهای قدیمی: همان کد اصلی شما
//     // از event delegation استفاده می‌کنیم تا برای سطرهای جدید هم کار کند
//     $('#productfeature_set-group').on('change', 'select[id^="id_product_features-"][id$="-feature"]', function() {
//         updateValues(this);
//     });
// });

if (typeof django !== 'undefined' && typeof django.jQuery !== 'undefined') {
    var $ = django.jQuery;
    $(document).ready(function () {

        function updateValues(featureDropdownElement) {
            var feature_id = $(featureDropdownElement).val();
            if (!feature_id) { return; }

            var id_attribute = $(featureDropdownElement).attr('id');
            var target_dropdown_id = id_attribute.replace("-feature", "-filter_value");
            var target_dropdown = $('#' + target_dropdown_id);
            var previously_selected_value = target_dropdown.data('original-value') || target_dropdown.val();

            $.ajax({
                type: "GET",
                url: "/products/ajax_admin/?feature_id=" + feature_id,
                success: function (res) {
                    var cols = document.getElementById(target_dropdown_id);
                    cols.options.length = 0;
                    $(cols).append(new Option("---------", ""));

                    for (var k in res) {
                        $(cols).append(new Option(k, res[k]));
                    }

                    if (previously_selected_value) {
                        $(cols).val(previously_selected_value);
                    }
                },
                error: function (xhr, status, error) {
                    console.error("Failed to fetch values:", status, error);
                }
            });
        }

        // --- بخش اجرایی ---

        // 1. برای سطرهای قدیمی: در زمان لود صفحه اجرا می‌شود (این بخش درست کار می‌کند)
        $('select[id^="id_product_features-"][id$="-feature"]').each(function() {
            updateValues(this);
            // رویداد change را هم به سطرهای فعلی متصل می‌کنیم
            $(this).on('change', function() {
                updateValues(this);
            });
        });

        // 2. برای سطرهای جدید: منتظر سیگنال جنگو می‌مانیم
        $(document).on('formset:added', function(event, $row, formsetName) {
            // چک می‌کنیم که این رویداد برای فرم‌ست صحیح باشد
            if (formsetName === 'productfeature_set') {
                // دراپ‌داون ویژگی را در سطر جدید پیدا می‌کنیم
                var newFeatureDropdown = $row.find('select[id$="-feature"]');
                // تابع آپدیت را به رویداد change آن متصل می‌کنیم
                newFeatureDropdown.on('change', function() {
                    updateValues(this);
                });
            }
        });

    });
}