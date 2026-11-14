# schema_report.R: describes every sheet of every Excel file in data/raw/ without printing any row.
# Run from the project root:   Rscript scripts/schema_report.R
# Output: artifacts/schema_report.txt (the only thing to share; check the "values:" lines first).

if (!requireNamespace("readxl", quietly = TRUE)) install.packages("readxl", repos = "https://cloud.r-project.org")
library(readxl)

dir        <- "data/raw"                    # put all .xlsx / .xls here (sub-folders are fine)
out        <- "artifacts/schema_report.txt"
max_levels <- 30                            # list distinct values of a text column only if <= this many (codes, labels); 0 = never
header_scan <- 20                           # rows scanned to find the real header under title rows

describe_col <- function(x, name) {
  nd  <- length(unique(x[!is.na(x)]))
  na_pct <- if (length(x)) 100 * mean(is.na(x)) else 0
  line <- sprintf("  - %s | %s | distinct=%d | NA=%.0f%%", name, class(x)[1], nd, na_pct)
  if (nd == 0) return(line)
  if (is.numeric(x)) {
    line <- paste0(line, sprintf(" | min=%s max=%s sum=%s", format(min(x, na.rm = TRUE)),
                                 format(max(x, na.rm = TRUE)), format(sum(x, na.rm = TRUE), big.mark = " ")))
  } else if (inherits(x, c("Date", "POSIXct"))) {
    line <- paste0(line, sprintf(" | from=%s to=%s", min(x, na.rm = TRUE), max(x, na.rm = TRUE)))
  } else if (is.character(x)) {
    len <- nchar(x[!is.na(x)])
    line <- paste0(line, sprintf(" | length %d-%d", min(len), max(len)))
    if (nd <= max_levels && max(len) <= 60) {   # long strings are free text: never listed
      tab <- sort(table(x), decreasing = TRUE)
      line <- paste0(line, "\n      values: ", paste(sprintf("%s (%d)", names(tab), as.integer(tab)), collapse = "; "))
    }
  }
  line
}

# The header is taken as the first of the top rows with the most non-empty cells (skips title/notes rows).
find_skip <- function(f, s) {
  raw <- suppressMessages(read_excel(f, sheet = s, col_names = FALSE, n_max = header_scan, .name_repair = "minimal"))
  if (nrow(raw) == 0) return(0)
  filled <- rowSums(!is.na(raw))
  which.max(filled) - 1
}

describe_sheet <- function(f, s) {
  skip <- find_skip(f, s)
  df <- suppressMessages(suppressWarnings(read_excel(f, sheet = s, skip = skip, guess_max = 10000)))
  c(sprintf("\n-- sheet: %s | %d rows x %d cols | header found after skipping %d row(s)", s, nrow(df), ncol(df), skip),
    vapply(seq_along(df), function(j) describe_col(df[[j]], names(df)[j]), ""))
}

files <- list.files(dir, pattern = "\\.xlsx?$", full.names = TRUE, recursive = TRUE, ignore.case = TRUE)
files <- files[!grepl("^~\\$", basename(files))]   # skip Excel lock files
if (!length(files)) stop("No .xlsx/.xls files found in ", dir)
dir.create(dirname(out), showWarnings = FALSE, recursive = TRUE)

con <- file(out, "w", encoding = "UTF-8")
writeLines(sprintf("Schema report | %s | %d files", format(Sys.time()), length(files)), con)
failed <- character()
for (i in seq_along(files)) {
  f <- files[i]
  rel <- sub(paste0("^", dir, "/"), "", f)
  message(sprintf("[%d/%d] %s", i, length(files), rel))
  writeLines(sprintf("\n========== %s (%.1f MB) ==========", rel, file.size(f) / 1e6), con)
  res <- tryCatch(unlist(lapply(excel_sheets(f), function(s)
           tryCatch(describe_sheet(f, s), error = function(e) sprintf("\n-- sheet: %s | ERROR: %s", s, conditionMessage(e))))),
         error = function(e) { failed <<- c(failed, rel); sprintf("ERROR opening file: %s", conditionMessage(e)) })
  writeLines(res, con)
}
if (length(failed)) writeLines(c("\n========== FILES THAT FAILED ==========", failed), con)
close(con)
message(sprintf("Done: %d files, %d failed -> %s", length(files), length(failed), out))
