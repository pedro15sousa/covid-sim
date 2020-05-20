#include "MicroCellPosition.hpp"
#include <stdexcept>

MicroCellPosition::MicroCellPosition(int x, int y)
	:x(x),
	y(y)
{}

MicroCellPosition MicroCellPosition::operator+(Direction direction) const {
	switch (direction) {
		case Right: return {this->x + 1, this->y};
		case Up: return {this->x, this->y - 1};
		case Left: return {this->x - 1, this->y};
		case Down: return {this->x, this->y + 1};
	}
	throw std::out_of_range("direction");
}
