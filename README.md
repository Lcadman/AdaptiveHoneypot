# AdaptiveHoneypot

AdaptiveHoneypot is contextual bandit with reinforcement learning project that dynamically optimizes the dwell time of cloud-based honeypot containers. Instead of relying on a fixed duration for honeypot deployment (e.g., 10 minutes), AdaptiveHoneypot analyzes real-time network traffic metrics to determine the optimal time to redeploy honeypots. This adaptive approach aims to maximize threat intelligence capture while minimizing resource use and maintaining an effective deception strategy.

## Table of Contents

- [Project Overview](#project-overview)
- [Key Objectives](#key-objectives)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)

## Project Overview

In modern cloud environments, attackers target honeypots expecting to find vulnerabilities, which makes it critical to deploy them intelligently. The primary goal of AdaptiveHoneypot is to use machine learning to decide when a honeypot has collected sufficient malicious activity and should be redeployed, instead of using a hard-coded time limit.

### Key Objectives

- **Dynamic Decision-Making:** Using a contextual bandit with reinforcement learning to continuously analyze honeypot traffic and decide the optimal redeployment time.
- **Data-Driven Optimization:** Leverage real-time network metrics (attack rate, unique IP counts, and interaction depth) to assess honeypot effectiveness.
- **Prototype Demonstration:** Deliver a functional prototype that integrates ML decision logic with automated honeypot redeployment in a cloud environment.

## Features

- **Honeypot Deployment:** Setup and configure a cloud-based honeypot (cowrie) to capture real-time network attack data.
- **Data Collection & Processing:** Log incoming connections and extract features such as attack rate and unique source count.
- **ML-Driven Dwell Time Optimization:** Train a model that determines when to redeploy the honeypot based on current traffic and engagement metrics.
- **Automated Redeployment:** Integrate the ML model with a controller that triggers honeypot redeployment via cloud APIs or container orchestration.
- **Evaluation & Visualization:** Compare the adaptive strategy to fixed-time strategies and visualize performance metrics (e.g., unique attack captures over time).

## Architecture

The project is divided into several key components:

1. **Honeypot Service:** The deployed service that logs incoming attack traffic.
2. **Data Collection Module:** Scripts that parse log files and extract relevant features.
3. **Machine Learning Module:** Contains the model (supervised learning or reinforcement learning) that predicts optimal redeployment times.
4. **Controller/Integration Module:** Automates the redeployment process based on the ML model's output.
5. **Evaluation & Visualization:** Tools to analyze and present the performance of the adaptive strategy compared to a static approach.

## Installation

### Prerequisites

- Python 3.7 or higher
- Cloud provider for managing honeypot instances (Fabric was used in this instance)
- Virtual environment tools

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/AdaptiveHoneypot.git
   cd AdaptiveHoneypot
   ```
