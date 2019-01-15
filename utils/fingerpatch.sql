-- phpMyAdmin SQL Dump
-- version 4.6.6deb5
-- https://www.phpmyadmin.net/
--
-- Host: localhost:3306
-- Generation Time: Jan 15, 2019 at 04:15 PM
-- Server version: 5.7.24-0ubuntu0.18.04.1
-- PHP Version: 7.2.10-0ubuntu0.18.04.1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `fingerpatch`
--

-- --------------------------------------------------------

--
-- Table structure for table `ubuntu_captures`
--

CREATE TABLE `ubuntu_captures` (
  `capture_id` int(11) NOT NULL,
  `truth_id` int(11) NOT NULL DEFAULT '-1',
  `already_captured` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `nb_flows` int(11) NOT NULL,
  `HTTP_Seq` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `Flows` text COLLATE utf8mb4_unicode_ci,
  `Payload_sent` text COLLATE utf8mb4_unicode_ci,
  `Payload_received` text COLLATE utf8mb4_unicode_ci,
  `http_succeed` tinyint(1) NOT NULL DEFAULT '0',
  `size_succeed` tinyint(1) NOT NULL DEFAULT '0',
  `http_found` text COLLATE utf8mb4_unicode_ci,
  `size_found` text COLLATE utf8mb4_unicode_ci,
  `size_ranking` int(11) DEFAULT NULL,
  `Processed` tinyint(1) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `ubuntu_cleaned_packets`
--

CREATE TABLE `ubuntu_cleaned_packets` (
  `id` int(11) NOT NULL,
  `Package` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `Version` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `Size` int(11) NOT NULL,
  `Filename` text COLLATE utf8mb4_unicode_ci,
  `Depends_Summing` int(11) NOT NULL,
  `Depends_Elements_involved` int(11) NOT NULL,
  `Depends_Childrens` varchar(9000) COLLATE utf8mb4_unicode_ci NOT NULL,
  `Depends_Frequency` int(11) NOT NULL,
  `Depends_Freq_in_p` float NOT NULL,
  `Recommends_Summing` int(11) NOT NULL,
  `Recommends_Elements_involved` int(11) NOT NULL,
  `Recommends_Childrens` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `Recommends_Frequency` int(11) NOT NULL,
  `Recommends_Freq_in_p` float NOT NULL,
  `Suggests_Summing` bigint(64) NOT NULL,
  `Suggests_Elements_involved` int(11) NOT NULL,
  `Suggests_Childrens` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `Suggests_Frequency` int(11) NOT NULL,
  `Suggests_Freq_in_p` float NOT NULL,
  `in` tinyint(1) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=COMPACT;

-- --------------------------------------------------------

--
-- Table structure for table `ubuntu_matched`
--

CREATE TABLE `ubuntu_matched` (
  `capture_id` int(11) NOT NULL,
  `package_id` int(11) NOT NULL,
  `Size_matched` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `ubuntu_packets`
--

CREATE TABLE `ubuntu_packets` (
  `id` int(11) NOT NULL,
  `capture_id` int(30) NOT NULL,
  `Package` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `Version` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `Architecture` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `Size` int(30) NOT NULL,
  `Installed-Size` int(30) NOT NULL,
  `Priority` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `Maintainer` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `SHA1` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `Description` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `parsedFrom` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `Description-md5` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `Bugs` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `Origin` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `MD5sum` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `Depends` text COLLATE utf8mb4_unicode_ci,
  `Recommends` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `Suggests` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `Homepage` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `Source` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `SHA256` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `Section` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `Supported` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `Filename` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `packageMode` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `in` tinyint(1) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Table structure for table `ubuntu_ready`
--

CREATE TABLE `ubuntu_ready` (
  `done` tinyint(1) NOT NULL,
  `id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `ubuntu_captures`
--
ALTER TABLE `ubuntu_captures`
  ADD PRIMARY KEY (`capture_id`);

--
-- Indexes for table `ubuntu_cleaned_packets`
--
ALTER TABLE `ubuntu_cleaned_packets`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `ubuntu_packets`
--
ALTER TABLE `ubuntu_packets`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `ubuntu_ready`
--
ALTER TABLE `ubuntu_ready`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `ubuntu_captures`
--
ALTER TABLE `ubuntu_captures`
  MODIFY `capture_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=211;
--
-- AUTO_INCREMENT for table `ubuntu_packets`
--
ALTER TABLE `ubuntu_packets`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=129537;
--
-- AUTO_INCREMENT for table `ubuntu_ready`
--
ALTER TABLE `ubuntu_ready`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
