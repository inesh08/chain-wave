# Phase 1: Problem Analysis & Data Architecture

## Problem Statement Analysis
Problem Statement P5: Centralized Monitoring addresses the absence of a centralized system that leads to stockouts, excess inventory, and high costs in supply chain management.

Key issues:
- Lack of real-time visibility across warehouses
- Inefficient inventory management
- Delayed response to demand fluctuations
- High carrying costs and stockout penalties

## Key Entities for Database
1. **Warehouses**: Locations storing inventory
2. **Products**: Items being managed
3. **Inventory Levels**: Current stock quantities
4. **Orders**: Customer or supplier orders
5. **Suppliers**: Providers of products

## Logical ER Diagram Schema
The ER diagram connects these entities to provide a 360-degree view:

- Warehouses have multiple Products (many-to-many via Inventory)
- Products are supplied by Suppliers (many-to-one)
- Orders reference Products and Warehouses
- Inventory tracks levels per Product per Warehouse

## Suggested KPIs
1. **Inventory Turnover Ratio**: Cost of goods sold / Average inventory value - Measures how quickly inventory is sold
2. **Stock-to-Sales Ratio**: Average inventory / Average monthly sales - Indicates inventory efficiency
3. **Stockout Rate**: Number of stockouts / Total orders - Percentage of orders affected by stockouts
4. **Excess Inventory Percentage**: (Current stock - Optimal stock) / Optimal stock - Identifies overstocking
5. **Days of Supply**: Current inventory / Average daily sales - Shows how many days inventory will last