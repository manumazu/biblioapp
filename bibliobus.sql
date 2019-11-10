-- phpMyAdmin SQL Dump
-- version 4.9.1
-- https://www.phpmyadmin.net/
--
-- Hôte : localhost
-- Généré le :  Dim 10 nov. 2019 à 16:22
-- Version du serveur :  10.3.17-MariaDB-0+deb10u1
-- Version de PHP :  7.3.9-1~deb10u1

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de données :  `bibliobus`
--
CREATE DATABASE IF NOT EXISTS `bibliobus` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `bibliobus`;

-- --------------------------------------------------------

--
-- Structure de la table `biblio_app`
--

CREATE TABLE `biblio_app` (
  `id` int(11) NOT NULL,
  `id_arduino` varchar(32) NOT NULL,
  `nb_lines` int(11) NOT NULL,
  `nb_cols` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Structure de la table `biblio_book`
--

CREATE TABLE `biblio_book` (
  `id` int(11) NOT NULL,
  `isbn` varchar(32) DEFAULT NULL,
  `title` varchar(255) NOT NULL,
  `author` varchar(255) NOT NULL,
  `editor` varchar(255) DEFAULT NULL,
  `year` varchar(10) DEFAULT NULL,
  `pages` varchar(10) DEFAULT NULL,
  `reference` varchar(32) DEFAULT NULL,
  `description` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Structure de la table `biblio_position`
--

CREATE TABLE `biblio_position` (
  `id_app` int(11) NOT NULL,
  `id_item` int(11) NOT NULL,
  `item_type` varchar(10) NOT NULL,
  `position` smallint(6) NOT NULL,
  `row` smallint(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Structure de la table `biblio_request`
--

CREATE TABLE `biblio_request` (
  `id_arduino` int(11) NOT NULL,
  `column` smallint(5) NOT NULL,
  `row` smallint(5) NOT NULL,
  `range` smallint(5) NOT NULL,
  `date_add` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Structure de la table `biblio_tags`
--

CREATE TABLE `biblio_tags` (
  `id` int(11) NOT NULL,
  `tag` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Structure de la table `biblio_tag_node`
--

CREATE TABLE `biblio_tag_node` (
  `node_type` varchar(10) NOT NULL,
  `id_node` int(11) NOT NULL,
  `id_tag` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `biblio_app`
--
ALTER TABLE `biblio_app`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `biblio_book`
--
ALTER TABLE `biblio_book`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `biblio_position`
--
ALTER TABLE `biblio_position`
  ADD UNIQUE KEY `id_app` (`id_app`,`id_item`,`item_type`),
  ADD KEY `id_item` (`id_item`,`position`,`row`);

--
-- Index pour la table `biblio_request`
--
ALTER TABLE `biblio_request`
  ADD UNIQUE KEY `id_arduino` (`id_arduino`,`column`,`row`);

--
-- Index pour la table `biblio_tags`
--
ALTER TABLE `biblio_tags`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `tag` (`tag`);

--
-- Index pour la table `biblio_tag_node`
--
ALTER TABLE `biblio_tag_node`
  ADD UNIQUE KEY `node_type` (`node_type`,`id_node`,`id_tag`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `biblio_app`
--
ALTER TABLE `biblio_app`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `biblio_book`
--
ALTER TABLE `biblio_book`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT pour la table `biblio_tags`
--
ALTER TABLE `biblio_tags`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;