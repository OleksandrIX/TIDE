function create_accordion_element(accordion_name, accordion_header_data, accordion_content_data) {
    const accordion = document.createElement("div");
    accordion.classList.add("accordion-container");
    accordion.classList.add(accordion_name);

    accordion.appendChild(render_accordion_header(accordion, accordion_header_data));
    accordion.appendChild(render_accordion_content(accordion_content_data));

    return accordion;
}

function render_accordion_header(accordion, accordion_header_data) {
    const accordion_header = document.createElement("div");
    accordion_header.classList.add("accordion-header");

    const accordion_header_content = document.createElement("div");
    accordion_header_content.classList.add("accordion-header-content");
    accordion_header_content.innerHTML = accordion_header_data;

    const arrow_up = document.createElement("img");
    arrow_up.classList.add("accordion-trigger");
    arrow_up.classList.add("arrow-up");
    arrow_up.src = "./assets/icons/arrow_up.svg";
    arrow_up.alt = "arrow up";
    arrow_up.addEventListener("click", (e) => toggle_accordion_trigger(e, accordion));

    const arrow_down = document.createElement("img");
    arrow_down.classList.add("accordion-trigger");
    arrow_down.classList.add("arrow-down");
    arrow_down.classList.add("active");
    arrow_down.src = "./assets/icons/arrow_down.svg";
    arrow_down.alt = "arrow down";
    arrow_down.addEventListener("click", (e) => toggle_accordion_trigger(e, accordion));

    accordion_header.appendChild(accordion_header_content);
    accordion_header.appendChild(arrow_up);
    accordion_header.appendChild(arrow_down);
    return accordion_header;
}

function render_accordion_content(accordion_content_data) {
    const accordion_content = document.createElement("div");
    accordion_content.classList.add("accordion-content");
    accordion_content.innerHTML = accordion_content_data;
    return accordion_content;
}

function toggle_accordion_trigger(e, accordion) {
    e.stopPropagation();
    const accordion_trigger_up = accordion.querySelector(".accordion-header>.accordion-trigger.arrow-up");
    const accordion_trigger_down = accordion.querySelector(".accordion-header>.accordion-trigger.arrow-down");
    const accordion_content = accordion.querySelector(".accordion-content");

    accordion_trigger_up.classList.toggle("active");
    accordion_trigger_down.classList.toggle("active");
    accordion_content.classList.toggle("active");
}
