function apply_accordion(accordion_name) {
    const accordions = Array.from(document.querySelectorAll(`.${accordion_name}`));
    new Accordion(accordions, {});
}
