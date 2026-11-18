"use strict";

// Sprint 3, Issue #25. Back-end authorization is pending completion of Issue #7.
(() => {
  const panel = document.getElementById("academic-goals-panel");
  const list = document.getElementById("academic-goals-list");
  const message = document.getElementById("goals-message");
  let activeStudentId = null;

  function reset() {
    activeStudentId = null;
    panel.hidden = true;
    list.replaceChildren();
    message.textContent = "";
  }

  const numberText = number => Number(number).toFixed(1).replace(/\.0$/, "");

  function makeElement(tag, className, value) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (value !== undefined) node.textContent = value;
    return node;
  }

  function renderCourse(studentId, course) {
    const item = makeElement("article", "academic-goal-item");
    const heading = makeElement("div", "academic-goal-heading");
    heading.appendChild(makeElement("strong", "", course.course_name));
    const status = {
      met: "Goal met",
      below_target: "Below goal",
      no_grades: "Awaiting grades",
      not_set: "No goal set",
    }[course.status] || "—";
    const pill = makeElement("span", "academic-goal-status " + course.status, status);
    heading.appendChild(pill);
    item.appendChild(heading);

    const current = course.current_average;
    const stats = makeElement("div", "academic-goal-summary");
    stats.appendChild(makeElement("span", "", current === null ? "Current: No grades yet" : `Current: ${numberText(current)}%`));
    stats.appendChild(makeElement("span", "", course.target_percentage === null ? "Goal: Not set" : `Goal: ${numberText(course.target_percentage)}%`));
    item.appendChild(stats);

    const track = makeElement("div", "academic-goal-track");
    track.setAttribute("role", "progressbar");
    track.setAttribute("aria-label", `${course.course_name} current average`);
    track.setAttribute("aria-valuemin", "0");
    track.setAttribute("aria-valuemax", "100");
    if (current !== null) {
      track.setAttribute("aria-valuenow", String(current));
      const fill = makeElement("div", "academic-goal-fill" + (course.status === "met" ? " met" : ""));
      fill.style.width = `${Math.max(0, Math.min(100, current))}%`;
      track.appendChild(fill);
    } else {
      track.setAttribute("aria-valuetext", "No grades yet");
    }
    item.appendChild(track);

    const form = makeElement("form", "academic-goal-form");
    const label = makeElement("label", "", `Target for ${course.course_name} (%)`);
    const field = makeElement("input", "");
    field.type = "number";
    field.step = "0.1";
    field.min = "0";
    field.max = "100";
    field.required = true;
    field.value = course.target_percentage ?? "";
    field.placeholder = "e.g. 90";
    const fieldId = `goal-course-${course.course_id}`;
    field.id = fieldId;
    label.htmlFor = fieldId;
    const save = makeElement("button", "", "Save goal");
    save.type = "submit";
    form.append(label, field, save);
    form.addEventListener("submit", async event => {
      event.preventDefault();
      if (!field.reportValidity()) return;
      const target = Number(field.value);
      if (!Number.isFinite(target) || target < 0 || target > 100) return;
      save.disabled = true;
      message.textContent = "Saving goal…";
      try {
        const response = await fetch(`/students/${studentId}/courses/${course.course_id}/goal`, {
          method: "PUT",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({target_percentage: target}),
        });
        if (!response.ok) throw new Error(`Unable to save goal (HTTP ${response.status}).`);
        message.textContent = "Goal saved successfully.";
        await load(studentId, true);
      } catch (error) {
        message.textContent = error.message;
      } finally {
        save.disabled = false;
      }
    });
    item.appendChild(form);
    return item;
  }

  async function load(studentId, preserveMessage = false) {
    activeStudentId = studentId;
    if (!preserveMessage) message.textContent = "Loading academic goals…";
    panel.hidden = false;
    try {
      const response = await fetch(`/students/${encodeURIComponent(studentId)}/goals`);
      if (!response.ok) throw new Error(`Unable to retrieve academic goals (HTTP ${response.status}).`);
      const data = await response.json();
      if (activeStudentId !== studentId) return;
      if (!data || !Array.isArray(data.courses)) throw new Error("Invalid goals response.");
      list.replaceChildren();
      if (data.courses.length === 0) {
        list.appendChild(makeElement("p", "goals-empty", "No courses enrolled yet."));
      } else {
        for (const course of data.courses) list.appendChild(renderCourse(studentId, course));
      }
      if (!preserveMessage) message.textContent = "";
    } catch (error) {
      if (activeStudentId === studentId) {
        list.replaceChildren();
        message.textContent = error.message || "Goals could not be loaded.";
      }
    }
  }

  window.GradeTrackerGoals = {load, reset};
})();
