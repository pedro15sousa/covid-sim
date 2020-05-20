#pragma once

#include "Direction.hpp"

class MicroCellPosition {
public:
	int x;
	int y;

	MicroCellPosition(int x, int y);

	MicroCellPosition operator+(Direction direction) const;
};

