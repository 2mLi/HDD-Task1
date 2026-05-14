library(tidyverse)

set.seed(123)


# =========================================================
# Read complete trajectories
# =========================================================

df <- read.csv(
  "https://raw.githubusercontent.com/2mLi/HDD-Task1/main/outputs/df.csv"
) %>%
  mutate(
    id = paste0("P", recovery_group + 1, "_", id + 1),
    
    trajectory = case_when(
      recovery_group == 0 ~ "Trajectory 1",
      recovery_group == 1 ~ "Trajectory 2",
      recovery_group == 2 ~ "Trajectory 3"
    )
  ) %>%
  select(id, day, steps, trajectory, recovery_group)


# =========================================================
# Simulation parameters
# =========================================================

followup_days <- 365

# ---------- Technical failure (MCAR) ----------
technical_failure_rate <- 0.02

# ---------- Device non-wear ----------
base_nonwear_rate <- 0.03
weekend_extra_nonwear <- 0.05
low_steps_extra_nonwear <- 0.08
low_steps_threshold <- 3000

# ---------- Compliance decay ----------
compliance_prob_early <- 0.02   # day 0–99
compliance_prob_mid   <- 0.06   # day 100–199
compliance_prob_late  <- 0.10   # day 200–299
compliance_prob_very_late <- 0.20  # day 300+

# ---------- Behavioural dropout ----------
dropout_day_1 <- 120
dropout_day_2 <- 200

dropout_prob_1 <- 0.10
dropout_prob_2 <- 0.30

dropout_gap_min <- 14
dropout_gap_max <- 35


# =========================================================
# Add missingness
# =========================================================

df_missing <- df %>%
  group_by(id) %>%
  mutate(
    weekday = day %% 7,
    weekend = weekday %in% c(5, 6),
    
    # ---------- MCAR ----------
    technical_failure =
      runif(n()) < technical_failure_rate,
    
    # ---------- Device non-wear ----------
    nonwear_prob =
      base_nonwear_rate +
      ifelse(weekend,
             weekend_extra_nonwear,
             0) +
      ifelse(steps < low_steps_threshold,
             low_steps_extra_nonwear,
             0),
    
    device_nonwear =
      runif(n()) < nonwear_prob,
    
    # ---------- Compliance decay ----------
    compliance_prob = case_when(
      day < 100 ~ compliance_prob_early,
      day < 200 ~ compliance_prob_mid,
      day < 300 ~ compliance_prob_late,
      day >= 300 ~ compliance_prob_very_late
    ),
    
    compliance_decay =
      runif(n()) < compliance_prob
  ) %>%
  ungroup()

# =========================================================
# Behavioural dropout gaps
# =========================================================

dropout_gaps <- df_missing %>%
  filter(
    day > dropout_day_1,
    steps < low_steps_threshold
  ) %>%
  mutate(
    dropout_prob = case_when(
      day > dropout_day_2 ~ dropout_prob_2,
      TRUE ~ dropout_prob_1
    )
  ) %>%
  filter(runif(n()) < dropout_prob) %>%
  group_by(id) %>%
  slice_sample(n = 1) %>%
  ungroup() %>%
  mutate(
    gap_start = day,
    gap_length = sample(dropout_gap_min:dropout_gap_max,
                        n(),
                        replace = TRUE),
    gap_end = gap_start + gap_length
  ) %>%
  select(id, gap_start, gap_end)

# =========================================================
# Apply missingness
# =========================================================

df_missing_final <- df_missing %>%
  left_join(dropout_gaps, by = "id") %>%
  mutate(
    behavioural_dropout =
      !is.na(gap_start) &
      day >= gap_start &
      day <= gap_end,
    
    is_missing =
      technical_failure |
      device_nonwear |
      compliance_decay |
      behavioural_dropout,
    
    steps_observed =
      ifelse(is_missing, NA, steps)
  )

# =========================================================
# Plot
# =========================================================
group_colors <- c(
  "P1_1" = "#99ccff",
  "P1_2" = "#66b2ff",
  "P1_3" = "#0066cc",
  
  "P2_4" = "#a8d5b0",
  "P2_5" = "#66bb6a",
  "P2_6" = "#1b5e20",
  
  "P3_7" = "#ffe08a",
  "P3_8" = "#ffa726",
  "P3_9" = "#e65100"
)


p <- ggplot() +
  
  # complete trajectory
  geom_line(
    data = df_missing_final,
    aes(
      x = day,
      y = steps,
      group = id,
      colour = id
    ),
    linetype = "dashed",
    alpha = 0.35,
    linewidth = 0.6
  ) +
  
  # observed trajectory
  geom_line(
    data = df_missing_final,
    aes(
      x = day,
      y = steps_observed,
      group = id,
      colour = id
    ),
    linewidth = 0.8,
    alpha = 0.9,
    na.rm = TRUE
  ) +
  
  scale_colour_manual(values = group_colors) +
  
  labs(
    x = "Days after treatment",
    y = "Daily step count",
    colour = "Patient",
    title = "Simulated trajectories with realistic missingness"
  ) +
  
  theme_minimal(base_size = 13) +
  
  theme(
    panel.grid.minor = element_blank(),
    legend.position = "bottom"
  )

# display plot
p

setwd("~/Desktop/Hackathon/missingness")

# save figure
ggsave(
  filename = "trajectory_missingness_plot.png",
  plot = p,
  width = 10,
  height = 6,
  dpi = 300
)

# save RDS
saveRDS(df_missing_final,"df_missing_final.rds")
