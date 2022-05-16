// Keyword Constructor
let KEYWORDS = [];
let counter = 0;
class Keyword {
  constructor(keyword, clientSpend, lastPosted, projectLength, unspecifiedJobs, hourlyRateMin, hourlyRateMax, paymentVerified, paymentUnverified, jobExpert, jobIntermediate, jobEntry, countries) {
    this.id = counter++;
    this.keyword = keyword;
    this.clientSpend = clientSpend;
    this.lastPosted = lastPosted;
    this.projectLength = projectLength;
    this.unspecifiedJobs = unspecifiedJobs;
    this.hourlyRateMin = hourlyRateMin;
    this.hourlyRateMax = hourlyRateMax;
    this.paymentVerified = paymentVerified;
    this.paymentUnverified = paymentUnverified;
    this.jobExpert = jobExpert;
    this.jobIntermediate = jobIntermediate;
    this.jobEntry = jobEntry;
    this.countries = countries;
  }
}

// UI Constructor
class UI {
  addKeywordToList = function (keyword) {
    const list = document.getElementById("keyword-list");
    // Create tr element
    const row = document.createElement("tr");
    row.id = keyword.id;
    // Insert cols
    row.innerHTML = `
      <td>${keyword.keyword}</td>
      <td>${keyword.clientSpend}</td>
      <td>${keyword.lastPosted}</td>
      <td><a href="#" class="ready">X<a></td>
    `;

    list.appendChild(row);
  };
  showAlert(message, className) {
    // Create div
    const div = document.createElement("div");
    // Add classes
    div.className = `alert ${className}`;
    // Add text
    div.appendChild(document.createTextNode(message));
    // Get parent
    const container = document.querySelector(".container");
    // Get form
    const form = document.querySelector("#scraper-form");
    // Insert alert
    container.insertBefore(div, form);

    // Timeout after 3 sec
    setTimeout(function () {
      document.querySelector(".alert").remove();
    }, 3000);
  }

  skipKeyword(target) {
    target.parentElement.parentElement.style.backgroundColor = "#EAEAEA";
    target.className = "skip";
    target.innerHTML = "➕";
  }

  addKeyword(target) {
    target.parentElement.parentElement.style.backgroundColor = "#FFFFFF";
    target.className = "ready";
    target.innerHTML = "X";
  }

  processKeyword(target) {
    target.parentElement.parentElement.style.backgroundColor = "#FFFFFF";
    target.className = "process";
    target.innerHTML = "";
    let loader = document.createElement("div");
    loader.classList.add('loading');
    target.appendChild(loader);
    // target.innerHTML = `<img src="https://c.tenor.com/hRBZHp-kE0MAAAAC/loading-circle-loading.gif" alt="Scraping..." height="3.5%" width="3.5%">`;
  }

  doneKeyword(target, { file }) {
    target.parentElement.parentElement.style.backgroundColor = "#9AE66E";
    target.className = "done";
    target.innerHTML = "🔽";
    target.href = file;
  }

  failKeyword(target) {
    target.parentElement.parentElement.style.backgroundColor = "#FC997C";
    target.className = "failed";
    target.innerHTML = "↺";
  }

  clearFields = function () {
    document.getElementById("keywords").value = "";
    let yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    let _mm = yesterday.getMonth()+1;
    let dd = yesterday.getDate().toString().length === 1 ? ('0' + yesterday.getDate().toString()) :  (yesterday.getDate().toString());
    let mm = _mm.toString().length === 1 ? ('0' + _mm.toString()) :  (_mm.toString());
    let yyyy = yesterday.getFullYear();
    document.getElementById("last-posted").value = yyyy + "-" + mm + "-" + dd;
    document.getElementById("client-spend").value = 20000;
    document.getElementsByName("project-zero")[0].checked = false;
    document.getElementsByName("project-short")[0].checked = false;
    document.getElementsByName("project-medium")[0].checked= true;
    document.getElementsByName("project-long")[0].checked= true;
    document.getElementById("unspecified-jobs").checked,
    document.getElementsByName("hourly-rate-min")[0].value = 20,
    document.getElementsByName("hourly-rate-max")[0].value = 40,
    document.getElementsByName("payment-verified")[0].checked= true,
    document.getElementsByName("payment-unverified")[0].checked,
    document.getElementsByName("job-expert")[0].checked= true,
    document.getElementsByName("job-intermediate")[0].checked= false,
    document.getElementsByName("job-entry")[0].checked= false,
    populateCountries();
  }
  isTableEmpty = function () {
    const table = document.getElementById("keyword-list");
    if (table.rows.length == 0) {
      return true;
    }
    for (let i = 0, row; (row = table.rows[i]); i++) {
      if (row.cells[3].firstChild.className.toString() === "ready") {
        return false;
      }
    }
    return true;
  };
}

const prepareScraping = () => {
  // Instantiate UI
  const ui = new UI();
  if (!ui.isTableEmpty()) {
    startScraping((elem, res, status) => {
      if (status) {
        ui.doneKeyword(elem, res);
      } else ui.failKeyword(elem);
      prepareScraping();
    });
  }
};

const startScraping = (callback) => {
  const table = document.getElementById("keyword-list");
  // get top unscraped keyword
  let topElement;
  for (let i = 0, row; (row = table.rows[i]); i++) {
    if (row.cells[3].firstChild.className.toString() === "ready") {
      topElement = row;
      break;
    }
  }
  const ui = new UI();
  ui.processKeyword(topElement.cells[3].firstChild);
  const k = KEYWORDS.find((e)=>{
    return e.id == topElement.id;
  })

  const data = {...k};
  console.log(JSON.stringify(data));
  const options = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  };

  fetch("/scrape", options)
    .then((response) => {
      if (!response.ok) {
        // make the promise be rejected if we didn't get a 2xx response
        let err = new Error(`Request failed for ${data.keyword}, code: ${response.status}`)
        if (response.status === 404) err = new Error(`No data found for ${data.keyword}, code: ${response.status}`)
        err.response = response;
        alert(err.message);
        throw err; 
      }
      return response.json()
    })
    .then((data) => {
      console.log("Success:", data);
      callback(topElement.cells[3].firstChild, data, true);
    })
    .catch((error) => {
      console.error("Error:", error);
      callback(topElement.cells[3].firstChild, error, false);
    });
};

// Event Listeners
document
  .getElementById("scraper-form")
  .addEventListener("submit", function (e) {
    // Get form values
    const keywords = document.getElementById("keywords").value,
      clientSpend = document.getElementById("client-spend").value,
      lastPosted = document.getElementById("last-posted").value,
      projectLength = {
        zero: document.getElementsByName("project-zero")[0].checked,
        short: document.getElementsByName("project-short")[0].checked,
        medium: document.getElementsByName("project-medium")[0].checked,
        long: document.getElementsByName("project-long")[0].checked
      },
      unspecifiedJobs = document.getElementById("unspecified-jobs").checked,
      hourlyRateMin = document.getElementsByName("hourly-rate-min")[0].value,
      hourlyRateMax = document.getElementsByName("hourly-rate-max")[0].value,
      paymentVerified = document.getElementsByName("payment-verified")[0].checked,
      paymentUnverified = document.getElementsByName("payment-unverified")[0].checked,
      jobExpert = document.getElementsByName("job-expert")[0].checked,
      jobIntermediate = document.getElementsByName("job-intermediate")[0].checked,
      jobEntry = document.getElementsByName("job-entry")[0].checked,
      countries = [...document.getElementById("grouped").children].map((e)=>{
        return e.firstElementChild.innerText;
      });


    let keywordList = [
      ...new Set(
        keywords
          .toString()
          .toLowerCase()
          .split("\n")
          .filter((e) => e)
      ),
    ];
    // Clear fields
    ui.clearFields();

    // Instantiate Keyword
    keywordList.forEach((k) => {
      k.trim();
      // Add Keyword to list
      k_obj = new Keyword(k, clientSpend, lastPosted, projectLength, unspecifiedJobs, hourlyRateMin, hourlyRateMax, paymentVerified, paymentUnverified, jobExpert, jobIntermediate, jobEntry, countries);
      KEYWORDS.push(k_obj);
      ui.addKeywordToList(k_obj);
    });

    // start scraping
    prepareScraping();

    e.preventDefault();
  });

// Event Listener for keywprd status
document.getElementById("keyword-list").addEventListener("click", function (e) {
  // Instantiate UI
  const ui = new UI();
  if (e.target.className === "ready") {
    // skip Keyword
    ui.skipKeyword(e.target);
    // Show message
    ui.showAlert("keyword Skipped!", "success");
  } else if (e.target.className === "skip" || e.target.className === "failed") {
    // add Keyword
    ui.addKeyword(e.target);
    // Show message
    ui.showAlert("keyword Added!", "success");
    prepareScraping();
  }
  if (e.target.className !== "done") {
    e.preventDefault();
  }
});

document.getElementById("reset-btn").addEventListener("click", function (e) {
  ui.clearFields();
  e.preventDefault();
})
// Main Content
const ui = new UI();
