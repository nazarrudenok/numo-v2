let mainContent = document.getElementsByClassName('main')[0].innerHTML;
let createContent = document.getElementsByClassName('create')[0].innerHTML;
let isContentChanged = false;

function create() {
    let main = document.getElementsByClassName('main')[0];
    let create = document.getElementsByClassName('create')[0];
    let logo = document.getElementsByClassName('logo')[0];
    
    if (isContentChanged) {
        // Повертаємо попередній контент
        main.innerHTML = mainContent;
        create.innerHTML = createContent;
        logo.style.opacity = '100%';
        icon.style.opacity = '100%';
    } else {
        // Зберігаємо поточний контент перед зміною
        mainContent = main.innerHTML;
        createContent = create.innerHTML;

        // Змінюємо вміст на форму
        main.innerHTML =
        `
        <div class="create-cont">
            <form action="/create" method="POST" class="create-form">
                <p class="create-title">Нова звичка</p>
                <div class="create-inputs-cont">
                    <input type="text" class="create-input" placeholder="Що за звичка?" name="title" autocomplete="off" required>
                    <textarea class="create-input" placeholder="Опишіть свою звичку.
Яка її роль у вашому житті?" name="description" autocomplete="off" required></textarea>
                    <input type="text" class="create-input"placeholder="Мета у днях. Рекомендуємо 30 днів" name="goal" autocomplete="off" required>
                    <input type="submit" value="Створити" class="btn-create">
                </div>
            </form>
        </div>
        ` 
        create.innerHTML = '<span class="material-symbols-outlined icon cancel">cancel</span>';
        logo.style.opacity = '0%';
        icon.style.opacity = '0%';
    }
    
    isContentChanged = !isContentChanged;
}
